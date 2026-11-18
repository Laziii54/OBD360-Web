using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Obd360.Api.Dtos;
using Obd360.Core.Entities;
using Obd360.Infrastructure.Data;

namespace Obd360.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/v1/vehicles")]
public class VehiclesController : ControllerBase
{
    private readonly ApplicationDbContext _db;

    public VehiclesController(ApplicationDbContext db)
    {
        _db = db;
    }

    [HttpGet]
    public async Task<ActionResult<IReadOnlyList<VehicleDto>>> List(CancellationToken cancellationToken)
    {
        var userId = User.GetUserId();

        var rows = await _db.Vehicles.AsNoTracking()
            .Where(vehicle => vehicle.UserId == userId)
            .OrderByDescending(vehicle => vehicle.CreatedAt)
            .Select(vehicle => new
            {
                Vehicle = vehicle,
                ScanCount = vehicle.ScanSessions.Count,
                LastScanAt = vehicle.ScanSessions.Max(session => (DateTime?)session.StartedAt)
            })
            .ToListAsync(cancellationToken);

        return rows
            .Select(row => ToDto(row.Vehicle, row.ScanCount, AsUtc(row.LastScanAt)))
            .ToList();
    }

    [HttpGet("{id:guid}")]
    public async Task<ActionResult<VehicleDto>> Get(Guid id, CancellationToken cancellationToken)
    {
        var userId = User.GetUserId();

        var row = await _db.Vehicles.AsNoTracking()
            .Where(vehicle => vehicle.Id == id && vehicle.UserId == userId)
            .Select(vehicle => new
            {
                Vehicle = vehicle,
                ScanCount = vehicle.ScanSessions.Count,
                LastScanAt = vehicle.ScanSessions.Max(session => (DateTime?)session.StartedAt)
            })
            .FirstOrDefaultAsync(cancellationToken);

        return row is null ? NotFound() : ToDto(row.Vehicle, row.ScanCount, AsUtc(row.LastScanAt));
    }

    [HttpPost]
    public async Task<ActionResult<VehicleDto>> Create(
        CreateVehicleRequest request,
        CancellationToken cancellationToken)
    {
        var userId = User.GetUserId();
        var vin = NormalizeVin(request.Vin);

        if (vin is not null &&
            await _db.Vehicles.AnyAsync(vehicle => vehicle.UserId == userId && vehicle.Vin == vin, cancellationToken))
        {
            return Conflict(new { message = "ამ VIN-ით მანქანა უკვე დამატებულია." });
        }

        var vehicle = new Vehicle
        {
            Id = Guid.NewGuid(),
            UserId = userId,
            Vin = vin,
            Make = request.Make.Trim(),
            Model = request.Model.Trim(),
            Year = request.Year,
            PlateNumber = NormalizeOptional(request.PlateNumber),
            CreatedAt = DateTime.UtcNow
        };

        _db.Vehicles.Add(vehicle);
        await _db.SaveChangesAsync(cancellationToken);

        return CreatedAtAction(
            nameof(Get),
            new { id = vehicle.Id },
            ToDto(vehicle, 0, null));
    }

    [HttpPut("{id:guid}")]
    public async Task<IActionResult> Update(
        Guid id,
        UpdateVehicleRequest request,
        CancellationToken cancellationToken)
    {
        var userId = User.GetUserId();
        var vehicle = await _db.Vehicles
            .FirstOrDefaultAsync(item => item.Id == id && item.UserId == userId, cancellationToken);

        if (vehicle is null)
        {
            return NotFound();
        }

        var vin = NormalizeVin(request.Vin);
        if (vin is not null &&
            await _db.Vehicles.AnyAsync(
                item => item.UserId == userId && item.Id != id && item.Vin == vin,
                cancellationToken))
        {
            return Conflict(new { message = "ამ VIN-ით მანქანა უკვე დამატებულია." });
        }

        vehicle.Vin = vin;
        vehicle.Make = request.Make.Trim();
        vehicle.Model = request.Model.Trim();
        vehicle.Year = request.Year;
        vehicle.PlateNumber = NormalizeOptional(request.PlateNumber);

        await _db.SaveChangesAsync(cancellationToken);
        return NoContent();
    }

    [HttpDelete("{id:guid}")]
    public async Task<IActionResult> Delete(Guid id, CancellationToken cancellationToken)
    {
        var userId = User.GetUserId();
        var vehicle = await _db.Vehicles
            .FirstOrDefaultAsync(item => item.Id == id && item.UserId == userId, cancellationToken);

        if (vehicle is null)
        {
            return NotFound();
        }

        // The database cascades scan sessions, reminders and reports for this vehicle.
        _db.Vehicles.Remove(vehicle);
        await _db.SaveChangesAsync(cancellationToken);
        return NoContent();
    }

    private static VehicleDto ToDto(Vehicle vehicle, int scanCount, DateTime? lastScanAt) =>
        new(
            vehicle.Id,
            vehicle.Vin,
            vehicle.Make,
            vehicle.Model,
            vehicle.Year,
            vehicle.PlateNumber,
            scanCount,
            lastScanAt,
            AsUtc(vehicle.CreatedAt));

    private static DateTime AsUtc(DateTime value) =>
        DateTime.SpecifyKind(value, DateTimeKind.Utc);

    private static DateTime? AsUtc(DateTime? value) =>
        value is { } date ? DateTime.SpecifyKind(date, DateTimeKind.Utc) : null;

    private static string? NormalizeVin(string? vin) =>
        string.IsNullOrWhiteSpace(vin)
            ? null
            : vin.Trim().ToUpperInvariant().Replace(" ", string.Empty);

    private static string? NormalizeOptional(string? value) =>
        string.IsNullOrWhiteSpace(value) ? null : value.Trim();
}
