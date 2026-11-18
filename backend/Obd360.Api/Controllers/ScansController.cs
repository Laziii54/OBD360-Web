using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Obd360.Api.Dtos;
using Obd360.Api.Integrations.N8n;
using Obd360.Core.Entities;
using Obd360.Core.Enums;
using Obd360.Infrastructure.Data;

namespace Obd360.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/v1/scans")]
public class ScansController : ControllerBase
{
    private const int HistoryLimit = 100;
    private const string UnknownVehicle = "Unknown vehicle";

    private readonly ApplicationDbContext _db;
    private readonly IN8nClient _n8n;
    private readonly ILogger<ScansController> _logger;

    public ScansController(
        ApplicationDbContext db,
        IN8nClient n8n,
        ILogger<ScansController> logger)
    {
        _db = db;
        _n8n = n8n;
        _logger = logger;
    }

    [HttpGet]
    public async Task<ActionResult<IReadOnlyList<ScanRecordDto>>> List()
    {
        var userId = User.GetUserId();

        var sessions = await _db.ScanSessions.AsNoTracking()
            .Where(s => s.Vehicle!.UserId == userId)
            .OrderByDescending(s => s.StartedAt)
            .Take(HistoryLimit)
            .Select(s => new
            {
                s.Id,
                s.Vehicle!.Model,
                s.Vehicle.Vin,
                s.StartedAt,
                s.EndedAt,
                Codes = s.DtcRecords.Select(d => d.Code).ToList()
            })
            .ToListAsync();

        return sessions
            .Select(s => new ScanRecordDto(
                s.Id,
                s.Model,
                s.Vin,
                DateTime.SpecifyKind(s.StartedAt, DateTimeKind.Utc),
                s.EndedAt is { } ended ? DateTime.SpecifyKind(ended, DateTimeKind.Utc) : null,
                s.Codes))
            .ToList();
    }

    [HttpPost]
    public async Task<IActionResult> Create(CreateScanRequest request)
    {
        var userId = User.GetUserId();
        var vin = string.IsNullOrWhiteSpace(request.Vin) ? null : request.Vin.Trim().ToUpperInvariant();

        var vehicle = await _db.Vehicles.FirstOrDefaultAsync(v => v.UserId == userId && v.Vin == vin);
        if (vehicle is null)
        {
            vehicle = new Vehicle
            {
                Id = Guid.NewGuid(),
                UserId = userId,
                Vin = vin,
                Make = "Unknown",
                Model = vin ?? UnknownVehicle
            };
            _db.Vehicles.Add(vehicle);
        }

        var session = new ScanSession
        {
            Id = Guid.NewGuid(),
            VehicleId = vehicle.Id,
            StartedAt = request.StartedAt.ToUniversalTime(),
            EndedAt = DateTime.UtcNow,
            ConnectionType = ConnectionType.Ble
        };

        foreach (var code in request.Codes.Distinct())
        {
            session.DtcRecords.Add(new DtcRecord { Id = Guid.NewGuid(), Code = code, Status = DtcStatus.Active });
        }

        _db.ScanSessions.Add(session);
        await _db.SaveChangesAsync();

        await NotifyCriticalCodesAsync(vehicle, session, request.Codes.Distinct().ToList());

        return NoContent();
    }

    private async Task NotifyCriticalCodesAsync(
        Vehicle vehicle,
        ScanSession session,
        IReadOnlyList<string> codes)
    {
        if (codes.Count == 0 || !_n8n.IsWorkflowConfigured(N8nWorkflow.DtcAlert))
        {
            return;
        }

        var vehicleName = vehicle.Make == "Unknown"
            ? vehicle.Model
            : $"{vehicle.Make} {vehicle.Model}".Trim();

        var payload = new
        {
            kind = "critical-dtc",
            vehicle = vehicleName,
            vin = vehicle.Vin,
            codes,
            scannedAt = session.StartedAt,
            email = User.FindFirstValue(ClaimTypes.Email)
        };

        try
        {
            // A notification must never block or fail the scan itself.
            using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(3));
            var result = await _n8n.SendAsync(N8nWorkflow.DtcAlert, payload, timeout.Token);

            if (!result.Success)
            {
                _logger.LogWarning(
                    "Critical DTC notification failed: {Error}",
                    result.Error);
            }
        }
        catch (OperationCanceledException)
        {
            _logger.LogWarning("Critical DTC notification timed out.");
        }
        catch (Exception exception)
        {
            _logger.LogWarning(exception, "Critical DTC notification failed.");
        }
    }
}

internal static class ClaimsPrincipalExtensions
{
    public static Guid GetUserId(this ClaimsPrincipal user) =>
        Guid.Parse(user.FindFirstValue(ClaimTypes.NameIdentifier) ?? user.FindFirstValue("sub")!);
}
