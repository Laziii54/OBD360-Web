using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Obd360.Api.Dtos;
using Obd360.Core.Entities;
using Obd360.Core.Enums;
using Obd360.Infrastructure.Data;

namespace Obd360.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/v1/preferences")]
public class PreferencesController : ControllerBase
{
    private readonly ApplicationDbContext _db;

    public PreferencesController(ApplicationDbContext db)
    {
        _db = db;
    }

    [HttpGet]
    public async Task<ActionResult<PreferencesDto>> Get()
    {
        var userId = User.GetUserId();
        var preference = await _db.UserPreferences.AsNoTracking().FirstOrDefaultAsync(p => p.UserId == userId);

        return new PreferencesDto(
            preference?.UnitSystem == UnitSystem.Imperial ? "imperial" : "metric");
    }

    [HttpPut]
    public async Task<IActionResult> Update(PreferencesDto request)
    {
        var userId = User.GetUserId();
        var preference = await _db.UserPreferences.FirstOrDefaultAsync(p => p.UserId == userId);
        if (preference is null)
        {
            preference = new UserPreference { UserId = userId };
            _db.UserPreferences.Add(preference);
        }

        preference.UnitSystem = request.UnitSystem == "imperial" ? UnitSystem.Imperial : UnitSystem.Metric;
        await _db.SaveChangesAsync();

        return NoContent();
    }
}
