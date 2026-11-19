using System.Security.Cryptography;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Obd360.Api.Dtos;
using Obd360.Api.Services;
using Obd360.Core.Entities;
using Obd360.Core.Enums;
using Obd360.Core.Interfaces;
using Obd360.Infrastructure.Data;
using Obd360.Infrastructure.Identity;

namespace Obd360.Api.Controllers;

[ApiController]
[Route("api/v1/auth")]
public class AuthController : ControllerBase
{
    private const string RefreshCookieName = "refreshToken";

    private readonly UserManager<ApplicationUser> _userManager;
    private readonly ApplicationDbContext _db;
    private readonly ITokenService _tokenService;
    private readonly IConfiguration _configuration;
    private readonly IEmailSender _emailSender;
    private readonly IPasswordResetCodeService _resetCodes;
    private readonly IWebHostEnvironment _environment;
    private readonly ILogger<AuthController> _logger;

    public AuthController(
        UserManager<ApplicationUser> userManager,
        ApplicationDbContext db,
        ITokenService tokenService,
        IConfiguration configuration,
        IEmailSender emailSender,
        IPasswordResetCodeService resetCodes,
        IWebHostEnvironment environment,
        ILogger<AuthController> logger)
    {
        _userManager = userManager;
        _db = db;
        _tokenService = tokenService;
        _configuration = configuration;
        _emailSender = emailSender;
        _resetCodes = resetCodes;
        _environment = environment;
        _logger = logger;
    }

    [HttpPost("register")]
    public async Task<ActionResult<AuthResponse>> Register(RegisterRequest request)
    {
        var existing = await _userManager.FindByEmailAsync(request.Email);
        if (existing is not null)
        {
            return Conflict(new { message = "ეს ელფოსტა უკვე დარეგისტრირებულია." });
        }

        var user = new ApplicationUser
        {
            UserName = request.Email,
            Email = request.Email,
            DisplayName = request.DisplayName,
            CreatedAt = DateTime.UtcNow
        };

        var result = await _userManager.CreateAsync(user, request.Password);
        if (!result.Succeeded)
        {
            return ValidationProblem(new ValidationProblemDetails(
                result.Errors.ToDictionary(e => e.Code, e => new[] { e.Description })));
        }

        await _userManager.AddToRoleAsync(user, "User");

        _db.UserPreferences.Add(new UserPreference
        {
            UserId = user.Id,
            UnitSystem = UnitSystem.Metric,
            Theme = AppTheme.Light,
            NotificationChannel = NotificationChannel.None
        });
        await _db.SaveChangesAsync();

        return await IssueTokensAsync(user);
    }

    [HttpPost("login")]
    public async Task<ActionResult<AuthResponse>> Login(LoginRequest request)
    {
        var user = await _userManager.FindByEmailAsync(request.Email);
        if (user is null || !await _userManager.CheckPasswordAsync(user, request.Password))
        {
            return Unauthorized(new { message = "არასწორი ელფოსტა ან პაროლი." });
        }

        return await IssueTokensAsync(user);
    }

    [HttpPost("refresh")]
    public async Task<ActionResult<AuthResponse>> Refresh()
    {
        if (!Request.Cookies.TryGetValue(RefreshCookieName, out var refreshToken) || string.IsNullOrEmpty(refreshToken))
        {
            return Unauthorized(new { message = "Refresh token არ არსებობს." });
        }

        var tokenHash = _tokenService.HashRefreshToken(refreshToken);
        var session = await _db.RefreshSessions
            .FirstOrDefaultAsync(s => s.TokenHash == tokenHash && s.RevokedAt == null);

        if (session is null || session.ExpiresAt < DateTime.UtcNow)
        {
            return Unauthorized(new { message = "Refresh token ვადაგასულია ან გაუქმებულია." });
        }

        var user = await _userManager.FindByIdAsync(session.UserId.ToString());
        if (user is null)
        {
            return Unauthorized();
        }

        session.RevokedAt = DateTime.UtcNow;
        return await IssueTokensAsync(user);
    }

    [HttpPost("logout")]
    public async Task<IActionResult> Logout()
    {
        if (Request.Cookies.TryGetValue(RefreshCookieName, out var refreshToken) && !string.IsNullOrEmpty(refreshToken))
        {
            var tokenHash = _tokenService.HashRefreshToken(refreshToken);
            var session = await _db.RefreshSessions.FirstOrDefaultAsync(s => s.TokenHash == tokenHash);
            if (session is not null)
            {
                session.RevokedAt = DateTime.UtcNow;
                await _db.SaveChangesAsync();
            }
        }

        Response.Cookies.Delete(RefreshCookieName);
        return NoContent();
    }

    [HttpPost("forgot-password")]
    public async Task<ActionResult<ForgotPasswordResponse>> ForgotPassword(ForgotPasswordRequest request)
    {
        const string genericMessage =
            "თუ ეს ელფოსტა დარეგისტრირებულია, პაროლის აღდგენის კოდი გამოგზავნილია.";

        var user = await _userManager.FindByEmailAsync(request.Email);
        string? devCode = null;

        if (user is not null)
        {
            var code = RandomNumberGenerator.GetInt32(0, 1_000_000).ToString("D6");
            var resetToken = await _userManager.GeneratePasswordResetTokenAsync(user);

            _resetCodes.Store(user.Email!, code, resetToken);

            try
            {
                var sent = await _emailSender.SendPasswordResetCodeAsync(
                    user.Email!,
                    user.DisplayName,
                    code);

                // Without SMTP the API logs the code. In development it is returned
                // to the browser so the flow can be demonstrated locally.
                if (!sent && _environment.IsDevelopment())
                {
                    devCode = code;
                }
            }
            catch (Exception exception)
            {
                _logger.LogError(exception, "Could not send the password-reset email for {Email}.", user.Email);

                if (_environment.IsDevelopment())
                {
                    devCode = code;
                }
            }
        }

        return Ok(new ForgotPasswordResponse(genericMessage, devCode));
    }

    [HttpPost("reset-password")]
    public async Task<IActionResult> ResetPassword(ResetPasswordRequest request)
    {
        var user = await _userManager.FindByEmailAsync(request.Email);
        if (user is null)
        {
            return BadRequest(new { message = "კოდი არასწორია ან ვადაგასულია." });
        }

        var validation = _resetCodes.Validate(user.Email!, request.Code);
        if (!validation.Success || validation.Token is null)
        {
            return BadRequest(new { message = validation.Error ?? "კოდი არასწორია ან ვადაგასულია." });
        }

        var result = await _userManager.ResetPasswordAsync(user, validation.Token, request.NewPassword);
        if (!result.Succeeded)
        {
            return ValidationProblem(new ValidationProblemDetails(
                result.Errors.ToDictionary(error => error.Code, error => new[] { error.Description })));
        }

        await RevokeRefreshSessionsAsync(user.Id);
        Response.Cookies.Delete(RefreshCookieName);

        return NoContent();
    }

    [Authorize]
    [HttpPost("change-password")]
    public async Task<IActionResult> ChangePassword(ChangePasswordRequest request)
    {
        var user = await _userManager.FindByIdAsync(User.GetUserId().ToString());
        if (user is null)
        {
            return Unauthorized();
        }

        var result = await _userManager.ChangePasswordAsync(
            user,
            request.CurrentPassword,
            request.NewPassword);

        if (!result.Succeeded)
        {
            return ValidationProblem(new ValidationProblemDetails(
                result.Errors.ToDictionary(error => error.Code, error => new[] { error.Description })));
        }

        await RevokeRefreshSessionsAsync(user.Id);
        Response.Cookies.Delete(RefreshCookieName);

        return NoContent();
    }

    private async Task RevokeRefreshSessionsAsync(Guid userId)
    {
        var sessions = await _db.RefreshSessions
            .Where(session => session.UserId == userId && session.RevokedAt == null)
            .ToListAsync();

        if (sessions.Count == 0)
        {
            return;
        }

        var revokedAt = DateTime.UtcNow;
        foreach (var session in sessions)
        {
            session.RevokedAt = revokedAt;
        }

        await _db.SaveChangesAsync();
    }

    private async Task<AuthResponse> IssueTokensAsync(ApplicationUser user)
    {
        var roles = await _userManager.GetRolesAsync(user);
        var accessToken = _tokenService.CreateAccessToken(user.Id, user.Email!, roles);
        var refreshToken = _tokenService.CreateRefreshToken();
        var refreshDays = _configuration.GetValue<int>("Jwt:RefreshTokenDays", 30);
        var expiresAt = DateTime.UtcNow.AddDays(refreshDays);

        _db.RefreshSessions.Add(new RefreshSession
        {
            Id = Guid.NewGuid(),
            UserId = user.Id,
            TokenHash = _tokenService.HashRefreshToken(refreshToken),
            ExpiresAt = expiresAt
        });
        await _db.SaveChangesAsync();

        Response.Cookies.Append(RefreshCookieName, refreshToken, new CookieOptions
        {
            HttpOnly = true,
            Secure = true,
            SameSite = SameSiteMode.Strict,
            Expires = expiresAt
        });

        return new AuthResponse(accessToken, user.Id, user.DisplayName, user.Email!, roles.ToList());
    }
}
