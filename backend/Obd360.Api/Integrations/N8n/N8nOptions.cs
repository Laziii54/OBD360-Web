namespace Obd360.Api.Integrations.N8n;

/// <summary>
/// Configuration for the n8n automation backend.
/// Bound from the "N8n" configuration section (appsettings, user secrets or environment variables).
/// </summary>
public sealed class N8nOptions
{
    public const string SectionName = "N8n";

    /// <summary>Origin of the n8n instance, for example "http://localhost:5678".</summary>
    public string BaseUrl { get; set; } = string.Empty;

    /// <summary>Webhook path used for the scan report workflow.</summary>
    public string ScanReportPath { get; set; } = "/webhook/obd360/scan-report";

    /// <summary>Webhook path used for the assistant follow-up questions.</summary>
    public string AskPath { get; set; } = "/webhook/obd360/ask";

    /// <summary>Webhook path used for critical DTC notifications.</summary>
    public string AlertPath { get; set; } = "/webhook/obd360/critical-dtc";

    /// <summary>Optional full webhook URL that overrides <see cref="BaseUrl"/> + <see cref="ScanReportPath"/>.</summary>
    public string WebhookUrl { get; set; } = string.Empty;

    /// <summary>Optional full webhook URL that overrides <see cref="BaseUrl"/> + <see cref="AskPath"/>.</summary>
    public string AskWebhookUrl { get; set; } = string.Empty;

    /// <summary>Optional full webhook URL that overrides <see cref="BaseUrl"/> + <see cref="AlertPath"/>.</summary>
    public string AlertWebhookUrl { get; set; } = string.Empty;

    /// <summary>Optional shared secret that is sent with every webhook call.</summary>
    public string WebhookToken { get; set; } = string.Empty;

    /// <summary>Header used to send <see cref="WebhookToken"/>.</summary>
    public string WebhookTokenHeader { get; set; } = "X-Webhook-Token";

    /// <summary>How long a single workflow call may take, in seconds.</summary>
    public int TimeoutSeconds { get; set; } = 90;

    /// <summary>How long the health probe may take, in seconds.</summary>
    public int HealthTimeoutSeconds { get; set; } = 3;

    public bool HasScanReportEndpoint =>
        !string.IsNullOrWhiteSpace(WebhookUrl) || !string.IsNullOrWhiteSpace(BaseUrl);

    public bool HasAskEndpoint =>
        !string.IsNullOrWhiteSpace(AskWebhookUrl) || !string.IsNullOrWhiteSpace(BaseUrl);

    public bool HasAlertEndpoint =>
        !string.IsNullOrWhiteSpace(AlertWebhookUrl) || !string.IsNullOrWhiteSpace(BaseUrl);

    public bool IsConfigured => HasScanReportEndpoint || HasAskEndpoint || HasAlertEndpoint;
}
