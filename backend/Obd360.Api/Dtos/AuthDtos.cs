using System.ComponentModel.DataAnnotations;

namespace Obd360.Api.Dtos;

public record RegisterRequest(
    [Required, StringLength(100, MinimumLength = 2)] string DisplayName,
    [Required, EmailAddress] string Email,
    [Required, MinLength(8)] string Password);

public record LoginRequest(
    [Required, EmailAddress] string Email,
    [Required] string Password);

public record AuthResponse(string AccessToken, Guid UserId, string DisplayName, string Email, IReadOnlyList<string> Roles);

public record ForgotPasswordRequest(
    [Required, EmailAddress] string Email);

public record ForgotPasswordResponse(
    string Message,
    string? DevResetUrl);

public record ResetPasswordRequest(
    [Required, EmailAddress] string Email,
    [Required] string Token,
    [Required, MinLength(8)] string NewPassword);

public record ChangePasswordRequest(
    [Required] string CurrentPassword,
    [Required, MinLength(8)] string NewPassword);
