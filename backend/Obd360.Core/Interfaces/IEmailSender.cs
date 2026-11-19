namespace Obd360.Core.Interfaces;

public interface IEmailSender
{
    /// <summary>
    /// Sends a password-reset link. Returns true when the message was handed to SMTP;
    /// false when email is not configured and the link was only logged (development).
    /// </summary>
    Task<bool> SendPasswordResetAsync(
        string toEmail,
        string displayName,
        string resetUrl,
        CancellationToken cancellationToken = default);
}
