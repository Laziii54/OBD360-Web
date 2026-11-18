using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Obd360.Api.Dtos;
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

    public AuthController(
        UserManager<ApplicationUser> userManager,
        ApplicationDbContext db,
        ITokenService tokenService,
        IConfiguration configuration)
    {
        _userManager = userManager;
        _db = db;
        _tokenService = tokenService;
        _configuration = configuration;
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
