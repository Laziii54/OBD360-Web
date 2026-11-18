using System.ComponentModel.DataAnnotations;

namespace Obd360.Api.Dtos;

public record ReminderDto(
    Guid Id,
    Guid VehicleId,
    string Vehicle,
    string Type,
    int? DueAtKm,
    DateOnly? DueAtDate,
    string Status);

public record CreateReminderRequest(
    Guid VehicleId,
    [Required, StringLength(80, MinimumLength = 2)] string Type,
    [Range(0, 2_000_000)] int? DueAtKm,
    DateOnly? DueAtDate);

public record UpdateReminderRequest(
    [Required, StringLength(80, MinimumLength = 2)] string Type,
    [Range(0, 2_000_000)] int? DueAtKm,
    DateOnly? DueAtDate,
    [RegularExpression("^(pending|overdue|done)$")] string? Status);
