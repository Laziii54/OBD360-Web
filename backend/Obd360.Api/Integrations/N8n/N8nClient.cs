using System.Net.Http.Json;
using System.Text.Encodings.Web;
using System.Text.Json;
using Microsoft.Extensions.Options;

namespace Obd360.Api.Integrations.N8n;

public enum N8nWorkflow
{
    ScanReport,
    Ask,
    DtcAlert
}

public sealed record N8nResult(bool Success, string? Text, string? Error, int StatusCode = 0)
{
    public static N8nResult Ok(string text, int statusCode) => new(true, text, null, statusCode);

    public static N8nResult Fail(string error, int statusCode = 0) => new(false, null, error, statusCode);
}

public interface IN8nClient
{
    bool IsConfigured { get; }

    bool IsWorkflowConfigured(N8nWorkflow workflow);

    Task<N8nResult> SendAsync(N8nWorkflow workflow, object payload, CancellationToken cancellationToken);

    /// <summary>Returns true when the n8n server answers, false when it is unreachable, null when there is no base URL to probe.</summary>
    Task<bool?> ProbeAsync(CancellationToken cancellationToken);
}

/// <summary>Thin, resilient HTTP client for the n8n webhook workflows used by OBD360.</summary>
public sealed class N8nClient : IN8nClient
{
    private const int MaxAttempts = 2;
    private static readonly TimeSpan RetryDelay = TimeSpan.FromMilliseconds(400);

    private static readonly JsonSerializerOptions JsonOptions = new(JsonSerializerDefaults.Web)
    {
        // Georgian prompts stay readable in n8n's execution view instead of \uXXXX escapes.
        Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping
    };

    private readonly HttpClient _http;
    private readonly N8nOptions _options;
    private readonly ILogger<N8nClient> _logger;

    public N8nClient(HttpClient http, IOptions<N8nOptions> options, ILogger<N8nClient> logger)
    {
        _http = http;
        _options = options.Value;
        _logger = logger;
    }

    public bool IsConfigured => _options.IsConfigured;

    public bool IsWorkflowConfigured(N8nWorkflow workflow) => workflow switch
    {
        N8nWorkflow.ScanReport => _options.HasScanReportEndpoint,
        N8nWorkflow.Ask => _options.HasAskEndpoint,
        N8nWorkflow.DtcAlert => _options.HasAlertEndpoint,
        _ => false
    };

    public async Task<N8nResult> SendAsync(
        N8nWorkflow workflow,
        object payload,
        CancellationToken cancellationToken)
    {
        var url = ResolveUrl(workflow);
        if (url is null)
        {
            return N8nResult.Fail(N8nMessages.NotConfigured);
        }

        using var timeout = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        timeout.CancelAfter(TimeSpan.FromSeconds(Math.Clamp(_options.TimeoutSeconds, 5, 300)));

        for (var attempt = 1; attempt <= MaxAttempts; attempt++)
        {
            try
            {
                using var request = new HttpRequestMessage(HttpMethod.Post, url)
                {
                    Content = JsonContent.Create(payload, payload.GetType(), options: JsonOptions)
                };

                AddWebhookToken(request);

                using var response = await _http.SendAsync(request, timeout.Token);
                var body = await response.Content.ReadAsStringAsync(timeout.Token);

                if (response.IsSuccessStatusCode)
                {
                    var statusCode = (int)response.StatusCode;
                    var text = N8nResponseParser.ExtractText(body);
                    if (text is null)
                    {
                        _logger.LogWarning(
                            "n8n workflow {Workflow} returned HTTP {StatusCode} without readable text.",
                            workflow,
                            statusCode);

                        return N8nResult.Fail(N8nMessages.EmptyResponse, statusCode);
                    }

                    return N8nResult.Ok(text, statusCode);
                }

                var errorCode = (int)response.StatusCode;
                if (errorCode >= 500 && attempt < MaxAttempts)
                {
                    _logger.LogWarning(
                        "n8n workflow {Workflow} returned HTTP {StatusCode}; retrying.",
                        workflow,
                        errorCode);

                    await Task.Delay(RetryDelay, timeout.Token);
                    continue;
                }

                _logger.LogWarning(
                    "n8n workflow {Workflow} returned HTTP {StatusCode}: {Body}",
                    workflow,
                    errorCode,
                    TrimForLog(body));

                return N8nResult.Fail(N8nMessages.HttpError(errorCode), errorCode);
            }
            catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested)
            {
                _logger.LogWarning(
                    "n8n workflow {Workflow} timed out after {Seconds}s.",
                    workflow,
                    _options.TimeoutSeconds);

                return N8nResult.Fail(N8nMessages.Timeout);
            }
            catch (HttpRequestException exception)
            {
                if (attempt < MaxAttempts)
                {
                    _logger.LogWarning(
                        exception,
                        "n8n workflow {Workflow} request failed; retrying.",
                        workflow);

                    try
                    {
                        await Task.Delay(RetryDelay, timeout.Token);
                    }
                    catch (OperationCanceledException)
                    {
                        return N8nResult.Fail(N8nMessages.Timeout);
                    }

                    continue;
                }

                _logger.LogWarning(exception, "n8n workflow {Workflow} request failed.", workflow);
                return N8nResult.Fail(N8nMessages.Unreachable);
            }
            catch (Exception exception) when (exception is JsonException or InvalidOperationException or NotSupportedException)
            {
                _logger.LogWarning(
                    exception,
                    "n8n workflow {Workflow} returned an unreadable response.",
                    workflow);

                return N8nResult.Fail(N8nMessages.UnreadableResponse);
            }
        }

        return N8nResult.Fail(N8nMessages.Unreachable);
    }

    public async Task<bool?> ProbeAsync(CancellationToken cancellationToken)
    {
        var baseUrl = _options.BaseUrl?.Trim();
        if (string.IsNullOrWhiteSpace(baseUrl) || !Uri.TryCreate(baseUrl, UriKind.Absolute, out _))
        {
            return null;
        }

        using var timeout = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        timeout.CancelAfter(TimeSpan.FromSeconds(Math.Clamp(_options.HealthTimeoutSeconds, 1, 15)));

        try
        {
            // Any HTTP response means that the n8n server is up, even if /healthz itself is disabled.
            using var response = await _http.GetAsync($"{baseUrl.TrimEnd('/')}/healthz", timeout.Token);
            return true;
        }
        catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested)
        {
            return false;
        }
        catch (HttpRequestException)
        {
            return false;
        }
    }

    private void AddWebhookToken(HttpRequestMessage request)
    {
        if (string.IsNullOrWhiteSpace(_options.WebhookToken))
        {
            return;
        }

        var headerName = string.IsNullOrWhiteSpace(_options.WebhookTokenHeader)
            ? "X-Webhook-Token"
            : _options.WebhookTokenHeader;

        request.Headers.TryAddWithoutValidation(headerName, _options.WebhookToken);
    }

    private string? ResolveUrl(N8nWorkflow workflow)
    {
        var explicitUrl = workflow switch
        {
            N8nWorkflow.ScanReport => _options.WebhookUrl,
            N8nWorkflow.Ask => _options.AskWebhookUrl,
            N8nWorkflow.DtcAlert => _options.AlertWebhookUrl,
            _ => string.Empty
        };

        if (!string.IsNullOrWhiteSpace(explicitUrl) &&
            Uri.TryCreate(explicitUrl.Trim(), UriKind.Absolute, out _))
        {
            return explicitUrl.Trim();
        }

        var baseUrl = _options.BaseUrl?.Trim();
        if (string.IsNullOrWhiteSpace(baseUrl) || !Uri.TryCreate(baseUrl, UriKind.Absolute, out _))
        {
            return null;
        }

        var path = workflow switch
        {
            N8nWorkflow.ScanReport => _options.ScanReportPath,
            N8nWorkflow.Ask => _options.AskPath,
            N8nWorkflow.DtcAlert => _options.AlertPath,
            _ => null
        };

        if (string.IsNullOrWhiteSpace(path))
        {
            return null;
        }

        return $"{baseUrl.TrimEnd('/')}/{path.TrimStart('/')}";
    }

    private static string TrimForLog(string body) =>
        body.Length <= 500 ? body : body[..500] + "...";
}
