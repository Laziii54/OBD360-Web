using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Obd360.Api.Dtos;
using Obd360.Infrastructure.Data;
using Obd360.Infrastructure.Identity;

namespace Obd360.Api.Controllers;

/// <summary>Administration endpoints for users, roles and diagnostic activity.</summary>
[ApiController]
[Authorize(Roles = "Admin")]
[Route("api/v1/admin")]
public class AdminController : ControllerBase
{
    private const int MaxRows = 200;

    private readonly ApplicationDbContext _db;
    private readonly UserManager<ApplicationUser> _users;
    private readonly ILogger<AdminController> _logger;

    public AdminController(
        ApplicationDbContext db,
        UserManager<ApplicationUser> users,
        ILogger<AdminController> logger)
    {
        _db = db;
        _users = users;
        _logger = logger;
    }

    /// <summary>Returns totals for users, vehicles, scans and DTC codes.</summary>
    [HttpGet("overview")]
    public async Task<ActionResult<AdminOverviewDto>> Overview(CancellationToken cancellationToken)
    {
        var users = await _users.Users.CountAsync(cancellationToken);
        var vehicles = await _db.Vehicles.CountAsync(cancellationToken);
        var scans = await _db.ScanSessions.CountAsync(cancellationToken);
        var dtcCodes = await _db.DtcCatalogEntries.CountAsync(cancellationToken);

        return new AdminOverviewDto(users, vehicles, scans, dtcCodes);
    }

    /// <summary>Lists users with roles, vehicle and scan counts. Optional name/email search.</summary>
    [HttpGet("users")]
    public async Task<ActionResult<IReadOnlyList<AdminUserDto>>> Users(
        [FromQuery] string? search,
        CancellationToken cancellationToken)
    {
        var term = search?.Trim();

        var query = _db.Users.AsNoTracking();

        if (!string.IsNullOrWhiteSpace(term))
        {
            query = query.Where(user =>
                user.DisplayName.Contains(term) ||
                (user.Email != null && user.Email.Contains(term)));
        }

        var rows = await query
            .OrderByDescending(user => user.CreatedAt)
            .Take(MaxRows)
            .Select(user => new
            {
                user.Id,
                user.DisplayName,
                Email = user.Email ?? string.Empty,
                user.CreatedAt,
                Vehicles = _db.Vehicles.Count(vehicle => vehicle.UserId == user.Id),
                Scans = _db.ScanSessions.Count(session => session.Vehicle!.UserId == user.Id),
                Roles = (
                    from userRole in _db.UserRoles
                    join role in _db.Roles on userRole.RoleId equals role.Id
                    where userRole.UserId == user.Id
                    select role.Name!
                ).ToList()
            })
            .ToListAsync(cancellationToken);

        return rows
            .Select(row => new AdminUserDto(
                row.Id,
                row.DisplayName,
                row.Email,
                row.Roles,
                row.Vehicles,
                row.Scans,
                DateTime.SpecifyKind(row.CreatedAt, DateTimeKind.Utc)))
            .ToList();
    }

    /// <summary>Deletes a user and their data. Cannot delete yourself or the last admin.</summary>
    [HttpDelete("users/{id:guid}")]
    public async Task<IActionResult> DeleteUser(Guid id, CancellationToken cancellationToken)
    {
        if (id == User.GetUserId())
        {
            return BadRequest(new { message = "საკუთარი ანგარიშის წაშლა ადმინის გვერდიდან შეუძლებელია." });
        }

        var user = await _users.FindByIdAsync(id.ToString());
        if (user is null)
        {
            return NotFound();
        }

        var roles = await _users.GetRolesAsync(user);
        if (roles.Contains("Admin") && await CountAdminsAsync(cancellationToken) <= 1)
        {
            return BadRequest(new { message = "ბოლო Admin-ის წაშლა შეუძლებელია." });
        }

        // Adapter has a Restrict FK to the user; remove it before deleting the account.
        await _db.Adapters
            .Where(adapter => adapter.UserId == id)
            .ExecuteDeleteAsync(cancellationToken);

        var result = await _users.DeleteAsync(user);
        if (!result.Succeeded)
        {
            return ValidationProblem(new ValidationProblemDetails(
                result.Errors.ToDictionary(error => error.Code, error => new[] { error.Description })));
        }

        _logger.LogWarning(
            "Admin {AdminEmail} deleted user {DeletedEmail}.",
            User.Identity?.Name,
            user.Email);

        return NoContent();
    }

    /// <summary>Adds or removes the Admin role for a user.</summary>
    [HttpPost("users/{id:guid}/toggle-role")]
    public async Task<ActionResult<AdminUserDto>> ToggleRole(Guid id, CancellationToken cancellationToken)
    {
        var user = await _users.FindByIdAsync(id.ToString());
        if (user is null)
        {
            return NotFound();
        }

        var roles = await _users.GetRolesAsync(user);
        var isAdmin = roles.Contains("Admin");

        if (isAdmin)
        {
            if (id == User.GetUserId())
            {
                return BadRequest(new { message = "საკუთარი Admin როლის მოხსნა შეუძლებელია." });
            }

            if (await CountAdminsAsync(cancellationToken) <= 1)
            {
                return BadRequest(new { message = "ბოლო Admin-ს როლი ვერ მოეხსნება." });
            }

            await _users.RemoveFromRoleAsync(user, "Admin");
        }
        else
        {
            await _users.AddToRoleAsync(user, "Admin");
        }

        roles = await _users.GetRolesAsync(user);
        _logger.LogInformation(
            "Admin {AdminEmail} changed roles for {UserEmail} to {Roles}.",
            User.Identity?.Name,
            user.Email,
            string.Join(", ", roles));

        return new AdminUserDto(
            user.Id,
            user.DisplayName,
            user.Email ?? string.Empty,
            roles.ToList(),
            await _db.Vehicles.CountAsync(vehicle => vehicle.UserId == user.Id, cancellationToken),
            await _db.ScanSessions.CountAsync(session => session.Vehicle!.UserId == user.Id, cancellationToken),
            DateTime.SpecifyKind(user.CreatedAt, DateTimeKind.Utc));
    }

    /// <summary>Lists recent scan sessions across all users. Optional user/vehicle/VIN search.</summary>
    [HttpGet("scans")]
    public async Task<ActionResult<IReadOnlyList<AdminScanDto>>> Scans(
        [FromQuery] string? search,
        CancellationToken cancellationToken)
    {
        var term = search?.Trim();

        var query =
            from session in _db.ScanSessions.AsNoTracking()
            join vehicle in _db.Vehicles.AsNoTracking() on session.VehicleId equals vehicle.Id
            join user in _db.Users.AsNoTracking() on vehicle.UserId equals user.Id
            select new
            {
                session.Id,
                session.StartedAt,
                session.EndedAt,
                User = user.DisplayName,
                Vehicle = vehicle.Make + " " + vehicle.Model,
                vehicle.Vin,
                Codes = session.DtcRecords.Select(record => record.Code).ToList()
            };

        if (!string.IsNullOrWhiteSpace(term))
        {
            query = query.Where(row =>
                row.User.Contains(term) ||
                row.Vehicle.Contains(term) ||
                (row.Vin != null && row.Vin.Contains(term)));
        }

        var rows = await query
            .OrderByDescending(row => row.StartedAt)
            .Take(MaxRows)
            .ToListAsync(cancellationToken);

        return rows
            .Select(row => new AdminScanDto(
                row.Id,
                DateTime.SpecifyKind(row.StartedAt, DateTimeKind.Utc),
                row.User,
                row.Vehicle,
                row.Vin,
                row.Codes,
                row.EndedAt is null ? "Failed" : "Completed"))
            .ToList();
    }

    private async Task<int> CountAdminsAsync(CancellationToken cancellationToken)
    {
        var adminRoleId = await _db.Roles
            .Where(role => role.Name == "Admin")
            .Select(role => role.Id)
            .FirstOrDefaultAsync(cancellationToken);

        return adminRoleId == Guid.Empty
            ? 0
            : await _db.UserRoles.CountAsync(
                userRole => userRole.RoleId == adminRoleId,
                cancellationToken);
    }
}
