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

    public async Task<bool> SendPasswordResetAsync(
        string toEmail,
        string displayName,
        string resetUrl,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(_options.Host) ||
            string.IsNullOrWhiteSpace(_options.FromAddress))
        {
            // Local development fallback: the link is printed to the API console.
            _logger.LogWarning(
                "SMTP is not configured. Password reset link for {Email}: {ResetUrl}",
                toEmail,
                resetUrl);
            return false;
        }

        var fromAddress = string.IsNullOrWhiteSpace(_options.FromAddress)
            ? _options.UserName
            : _options.FromAddress;

        var safeName = WebUtility.HtmlEncode(displayName);
        var safeUrl = WebUtility.HtmlEncode(resetUrl);

        using var message = new MailMessage
        {
            From = new MailAddress(fromAddress, _options.FromName),
            Subject = "OBD360 — პაროლის აღდგენა",
            IsBodyHtml = true,
            Body = $"""
                <div style="font-family:Segoe UI,Arial,sans-serif;color:#20251f;line-height:1.6">
                  <h2 style="font-weight:800">OBD360</h2>
                  <p>გამარჯობა, {safeName}.</p>
                  <p>მივიღეთ თქვენი ანგარიშის პაროლის აღდგენის მოთხოვნა. ახალი პაროლის დასაყენებლად გახსენით ბმული:</p>
                  <p><a href="{safeUrl}" style="color:#3f5d4e;font-weight:700">პაროლის აღდგენა</a></p>
                  <p style="color:#72776e;font-size:13px">ბმული მოქმედებს 1 საათი. თუ მოთხოვნა თქვენ არ გამოგიგზავნიათ, უგულებელყავით ეს წერილი.</p>
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
