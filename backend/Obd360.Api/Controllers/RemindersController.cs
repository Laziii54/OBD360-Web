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
[Route("api/v1/reminders")]
public class RemindersController : ControllerBase
{
    private readonly ApplicationDbContext _db;

    public RemindersController(ApplicationDbContext db)
    {
        _db = db;
    }

    [HttpGet]
    public async Task<ActionResult<IReadOnlyList<ReminderDto>>> List(
        [FromQuery] Guid? vehicleId,
        CancellationToken cancellationToken)
    {
        var userId = User.GetUserId();

        var query = _db.MaintenanceReminders.AsNoTracking()
            .Where(reminder => reminder.Vehicle!.UserId == userId);

        if (vehicleId is { } id && id != Guid.Empty)
        {
            query = query.Where(reminder => reminder.VehicleId == id);
        }

        var rows = await query
            .OrderBy(reminder => reminder.DueAtDate == null)
            .ThenBy(reminder => reminder.DueAtDate)
            .ThenBy(reminder => reminder.DueAtKm)
            .Select(reminder => new
            {
                reminder.Id,
                reminder.VehicleId,
                Vehicle = reminder.Vehicle!.Make + " " + reminder.Vehicle.Model,
                reminder.Type,
                reminder.DueAtKm,
                reminder.DueAtDate,
                reminder.Status
            })
            .ToListAsync(cancellationToken);

        var today = DateOnly.FromDateTime(DateTime.UtcNow);

        return rows
            .Select(row => new ReminderDto(
                row.Id,
                row.VehicleId,
                row.Vehicle,
                row.Type,
                row.DueAtKm,
                row.DueAtDate,
                ResolveStatus(row.Status, row.DueAtDate, today)))
            .ToList();
    }

    [HttpPost]
    public async Task<ActionResult<ReminderDto>> Create(
        CreateReminderRequest request,
        CancellationToken cancellationToken)
    {
        var userId = User.GetUserId();

        var vehicle = await _db.Vehicles.AsNoTracking()
            .FirstOrDefaultAsync(item => item.Id == request.VehicleId && item.UserId == userId, cancellationToken);

        if (vehicle is null)
        {
            return NotFound(new { message = "მანქანა ვერ მოიძებნა." });
        }

        var reminder = new MaintenanceReminder
        {
            Id = Guid.NewGuid(),
            VehicleId = vehicle.Id,
            Type = request.Type.Trim(),
            DueAtKm = request.DueAtKm,
            DueAtDate = request.DueAtDate,
            Status = ReminderStatus.Pending
        };

        _db.MaintenanceReminders.Add(reminder);
        await _db.SaveChangesAsync(cancellationToken);

        return CreatedAtAction(
            nameof(List),
            new { vehicleId = reminder.VehicleId },
            new ReminderDto(
                reminder.Id,
                reminder.VehicleId,
                $"{vehicle.Make} {vehicle.Model}",
                reminder.Type,
                reminder.DueAtKm,
                reminder.DueAtDate,
                "pending"));
    }

    [HttpPut("{id:guid}")]
    public async Task<IActionResult> Update(
        Guid id,
        UpdateReminderRequest request,
        CancellationToken cancellationToken)
    {
        var userId = User.GetUserId();
        var reminder = await _db.MaintenanceReminders
            .FirstOrDefaultAsync(
                item => item.Id == id && item.Vehicle!.UserId == userId,
                cancellationToken);

        if (reminder is null)
        {
            return NotFound();
        }

        reminder.Type = request.Type.Trim();
        reminder.DueAtKm = request.DueAtKm;
        reminder.DueAtDate = request.DueAtDate;

        if (!string.IsNullOrWhiteSpace(request.Status))
        {
            reminder.Status = ParseStatus(request.Status);
        }

        await _db.SaveChangesAsync(cancellationToken);
        return NoContent();
    }

    [HttpPost("{id:guid}/complete")]
    public async Task<IActionResult> Complete(Guid id, CancellationToken cancellationToken)
    {
        var userId = User.GetUserId();
        var reminder = await _db.MaintenanceReminders
            .FirstOrDefaultAsync(
                item => item.Id == id && item.Vehicle!.UserId == userId,
                cancellationToken);

        if (reminder is null)
        {
            return NotFound();
        }

        reminder.Status = ReminderStatus.Done;
        await _db.SaveChangesAsync(cancellationToken);
        return NoContent();
    }

    [HttpDelete("{id:guid}")]
    public async Task<IActionResult> Delete(Guid id, CancellationToken cancellationToken)
    {
        var userId = User.GetUserId();
        var reminder = await _db.MaintenanceReminders
            .FirstOrDefaultAsync(
                item => item.Id == id && item.Vehicle!.UserId == userId,
                cancellationToken);

        if (reminder is null)
        {
            return NotFound();
        }

        _db.MaintenanceReminders.Remove(reminder);
        await _db.SaveChangesAsync(cancellationToken);
        return NoContent();
    }

    private static string ResolveStatus(ReminderStatus status, DateOnly? dueAtDate, DateOnly today) =>
        status switch
        {
            ReminderStatus.Done => "done",
            ReminderStatus.Overdue => "overdue",
            _ when dueAtDate is { } date && date < today => "overdue",
            _ => "pending"
        };

    private static ReminderStatus ParseStatus(string value) =>
        value.Trim().ToLowerInvariant() switch
        {
            "done" => ReminderStatus.Done,
            "overdue" => ReminderStatus.Overdue,
            _ => ReminderStatus.Pending
        };
}
