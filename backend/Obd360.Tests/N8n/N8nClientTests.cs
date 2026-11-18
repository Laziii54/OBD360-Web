using System.Net;
using System.Text;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Options;
using Obd360.Api.Integrations.N8n;

namespace Obd360.Tests.N8n;

public class N8nClientTests
{
    private static N8nOptions Options(Action<N8nOptions>? configure = null)
    {
        var options = new N8nOptions
        {
            BaseUrl = "http://n8n.local",
            TimeoutSeconds = 5,
            HealthTimeoutSeconds = 1
        };

        configure?.Invoke(options);
        return options;
    }

    private static N8nClient CreateClient(StubHandler handler, N8nOptions options) =>
        new(
            new HttpClient(handler) { Timeout = Timeout.InfiniteTimeSpan },
            Microsoft.Extensions.Options.Options.Create(options),
            NullLogger<N8nClient>.Instance);

    private static HttpResponseMessage Json(HttpStatusCode statusCode, string body) =>
        new(statusCode)
        {
            Content = new StringContent(body, Encoding.UTF8, "application/json")
        };

    [Fact]
    public async Task SendAsync_Fails_WhenN8nIsNotConfigured()
    {
        var handler = new StubHandler(_ => throw new InvalidOperationException("HTTP must not be called."));
        var client = CreateClient(handler, Options(options => options.BaseUrl = ""));

        var result = await client.SendAsync(
            N8nWorkflow.ScanReport,
            new { prompt = "test" },
            CancellationToken.None);

        Assert.False(result.Success);
        Assert.Equal(N8nMessages.NotConfigured, result.Error);
        Assert.Equal(0, handler.CallCount);
    }

    [Fact]
    public async Task SendAsync_PostsToScanReportWebhookAndReadsText()
    {
        var handler = new StubHandler(_ => Json(HttpStatusCode.OK, """{"text":"ანგარიში","model":"claude"}"""));
        var client = CreateClient(handler, Options(options => options.WebhookToken = "secret"));

        var result = await client.SendAsync(
            N8nWorkflow.ScanReport,
            new { prompt = "შემამოწმე კოდი" },
            CancellationToken.None);

        Assert.True(result.Success);
        Assert.Equal("ანგარიში", result.Text);
        Assert.Equal(HttpMethod.Post, handler.LastMethod);
        Assert.Equal("http://n8n.local/webhook/obd360/scan-report", handler.LastUri?.ToString());
        Assert.Equal("secret", handler.LastToken);
        Assert.Contains("\"prompt\":\"შემამოწმე კოდი\"", handler.LastBody);
    }

    [Fact]
    public async Task SendAsync_UsesExplicitWebhookUrl_WhenProvided()
    {
        var handler = new StubHandler(_ => Json(HttpStatusCode.OK, """{"answer":"კითხვის პასუხი"}"""));
        var client = CreateClient(
            handler,
            Options(options =>
            {
                options.BaseUrl = "";
                options.AskWebhookUrl = "https://hooks.example.com/ask";
            }));

        var result = await client.SendAsync(
            N8nWorkflow.Ask,
            new { prompt = "რატომ?" },
            CancellationToken.None);

        Assert.True(result.Success);
        Assert.Equal("კითხვის პასუხი", result.Text);
        Assert.Equal("https://hooks.example.com/ask", handler.LastUri?.ToString());
    }

    [Fact]
    public async Task SendAsync_RetriesServerErrors_ThenFails()
    {
        var handler = new StubHandler(_ => Json(HttpStatusCode.InternalServerError, """{"message":"boom"}"""));
        var client = CreateClient(handler, Options());

        var result = await client.SendAsync(
            N8nWorkflow.ScanReport,
            new { prompt = "test" },
            CancellationToken.None);

        Assert.False(result.Success);
        Assert.Equal(500, result.StatusCode);
        Assert.Equal(2, handler.CallCount);
        Assert.Equal(N8nMessages.HttpError(500), result.Error);
    }

    [Fact]
    public async Task SendAsync_DoesNotRetryClientErrors()
    {
        var handler = new StubHandler(_ => Json(HttpStatusCode.NotFound, """{"message":"not found"}"""));
        var client = CreateClient(handler, Options());

        var result = await client.SendAsync(
            N8nWorkflow.ScanReport,
            new { prompt = "test" },
            CancellationToken.None);

        Assert.False(result.Success);
        Assert.Equal(404, result.StatusCode);
        Assert.Equal(1, handler.CallCount);
    }

    [Fact]
    public async Task SendAsync_ReportsEmptyResponse_WhenWorkflowReturnsNoText()
    {
        var handler = new StubHandler(_ => Json(HttpStatusCode.OK, ""));
        var client = CreateClient(handler, Options());

        var result = await client.SendAsync(
            N8nWorkflow.ScanReport,
            new { prompt = "test" },
            CancellationToken.None);

        Assert.False(result.Success);
        Assert.Equal(N8nMessages.EmptyResponse, result.Error);
    }

    [Fact]
    public async Task ProbeAsync_ReturnsTrue_WhenServerAnswers()
    {
        var handler = new StubHandler(_ => Json(HttpStatusCode.NotFound, "not found"));
        var client = CreateClient(handler, Options());

        var reachable = await client.ProbeAsync(CancellationToken.None);

        Assert.True(reachable);
        Assert.Equal("http://n8n.local/healthz", handler.LastUri?.ToString());
    }

    [Fact]
    public async Task ProbeAsync_ReturnsFalse_WhenServerIsUnreachable()
    {
        var handler = new StubHandler(_ => throw new HttpRequestException("connection refused"));
        var client = CreateClient(handler, Options());

        var reachable = await client.ProbeAsync(CancellationToken.None);

        Assert.False(reachable);
    }

    [Fact]
    public async Task ProbeAsync_ReturnsNull_WithoutBaseUrl()
    {
        var handler = new StubHandler(_ => throw new InvalidOperationException("HTTP must not be called."));
        var client = CreateClient(handler, Options(options => options.BaseUrl = ""));

        Assert.Null(await client.ProbeAsync(CancellationToken.None));
        Assert.Equal(0, handler.CallCount);
    }

    private sealed class StubHandler : HttpMessageHandler
    {
        private readonly Func<HttpRequestMessage, HttpResponseMessage> _respond;

        public StubHandler(Func<HttpRequestMessage, HttpResponseMessage> respond) => _respond = respond;

        public int CallCount { get; private set; }

        public Uri? LastUri { get; private set; }

        public HttpMethod? LastMethod { get; private set; }

        public string? LastBody { get; private set; }

        public string? LastToken { get; private set; }

        protected override Task<HttpResponseMessage> SendAsync(
            HttpRequestMessage request,
            CancellationToken cancellationToken)
        {
            CallCount++;
            LastUri = request.RequestUri;
            LastMethod = request.Method;
            LastBody = request.Content?.ReadAsStringAsync(cancellationToken).GetAwaiter().GetResult();
            LastToken = request.Headers.TryGetValues("X-Webhook-Token", out var values)
                ? values.FirstOrDefault()
                : null;

            return Task.FromResult(_respond(request));
        }
    }
}
