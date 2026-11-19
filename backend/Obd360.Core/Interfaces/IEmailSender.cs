namespace Obd360.Core.Interfaces;

public interface IEmailSender
{
    /// <summary>
    /// Sends a six-digit password-reset code. Returns true when the message was handed to SMTP;
    /// false when email is not configured and the code was only logged (development).
    /// </summary>
    Task<bool> SendPasswordResetCodeAsync(
        string toEmail,
        string displayName,
        string code,
        CancellationToken cancellationToken = default);

    Task<bool> SendReminderEmailAsync(
        string toEmail,
        string displayName,
        IReadOnlyList<string> reminders,
        CancellationToken cancellationToken = default);
}
