using System.Net;
using System.Net.Mail;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Obd360.Core.Interfaces;

namespace Obd360.Infrastructure.Services;

public sealed class SmtpEmailSender : IEmailSender
{
    private readonly SmtpOptions _options;
    private readonly ILogger<SmtpEmailSender> _logger;

    public SmtpEmailSender(IOptions<SmtpOptions> options, ILogger<SmtpEmailSender> logger)
    {
        _options = options.Value;
        _logger = logger;
    }

    public async Task<bool> SendPasswordResetCodeAsync(
        string toEmail,
        string displayName,
        string code,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(_options.Host) ||
            string.IsNullOrWhiteSpace(_options.FromAddress))
        {
            // Local development fallback: the code is printed to the API console.
            _logger.LogWarning(
                "SMTP is not configured. Password reset code for {Email}: {Code}",
                toEmail,
                code);
            return false;
        }

        var fromAddress = string.IsNullOrWhiteSpace(_options.FromAddress)
            ? _options.UserName
            : _options.FromAddress;

        var safeName = WebUtility.HtmlEncode(displayName);
        var safeCode = WebUtility.HtmlEncode(code);

        using var message = new MailMessage
        {
            From = new MailAddress(fromAddress, _options.FromName),
            Subject = "OBD360 — პაროლის აღდგენის კოდი",
            IsBodyHtml = true,
            Body = $"""
                <div style="font-family:Segoe UI,Arial,sans-serif;color:#20251f;line-height:1.6">
                  <h2 style="font-weight:800">OBD360</h2>
                  <p>გამარჯობა, {safeName}.</p>
                  <p>პაროლის აღდგენისთვის შეიყვანე ეს კოდი:</p>
                  <p style="font-size:30px;font-weight:800;letter-spacing:8px;color:#3f5d4e">{safeCode}</p>
                  <p style="color:#72776e;font-size:13px">კოდი მოქმედებს 10 წუთი და გამოიყენება მხოლოდ ერთხელ. თუ მოთხოვნა თქვენ არ გამოგიგზავნიათ, უგულებელყავით ეს წერილი.</p>
                </div>
                """
        };

        message.To.Add(toEmail);

        using var client = new SmtpClient(_options.Host, _options.Port)
        {
            EnableSsl = _options.EnableSsl,
            Credentials = string.IsNullOrWhiteSpace(_options.UserName)
                ? CredentialCache.DefaultNetworkCredentials
                : new NetworkCredential(_options.UserName, _options.Password)
        };

        await client.SendMailAsync(message, cancellationToken);
        return true;
    }

    public async Task<bool> SendReminderEmailAsync(
        string toEmail,
        string displayName,
        IReadOnlyList<string> reminders,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(_options.Host) ||
            string.IsNullOrWhiteSpace(_options.FromAddress))
        {
            _logger.LogWarning(
                "SMTP is not configured. Reminder email for {Email} was not sent: {Reminders}",
                toEmail,
                string.Join(", ", reminders));
            return false;
        }

        var fromAddress = string.IsNullOrWhiteSpace(_options.FromAddress)
            ? _options.UserName
            : _options.FromAddress;

        var safeName = WebUtility.HtmlEncode(displayName);
        var items = string.Join(
            string.Empty,
            reminders.Select(reminder => $"<li>{WebUtility.HtmlEncode(reminder)}</li>"));

        using var message = new MailMessage
        {
            From = new MailAddress(fromAddress, _options.FromName),
            Subject = "OBD360 — ტექნიკური მომსახურების შეხსენება",
            IsBodyHtml = true,
            Body = $"""
                <div style="font-family:Segoe UI,Arial,sans-serif;color:#20251f;line-height:1.6">
                  <h2 style="font-weight:800">OBD360</h2>
                  <p>გამარჯობა, {safeName}.</p>
                  <p>შემდეგი ტექნიკური მომსახურება ვადაგასულია ან დღეს იწურება:</p>
                  <ul>{items}</ul>
                  <p><a href="http://localhost:4200/app/reminders" style="color:#3f5d4e;font-weight:700">Reminders-ის გახსნა</a></p>
                  <p style="color:#72776e;font-size:13px">შეტყობინება გამოგზავნილია OBD360-ის მიერ.</p>
                </div>
                """
        };

        message.To.Add(toEmail);

        using var client = new SmtpClient(_options.Host, _options.Port)
        {
            EnableSsl = _options.EnableSsl,
            Credentials = string.IsNullOrWhiteSpace(_options.UserName)
                ? CredentialCache.DefaultNetworkCredentials
                : new NetworkCredential(_options.UserName, _options.Password)
        };

        await client.SendMailAsync(message, cancellationToken);
        return true;
    }
}
