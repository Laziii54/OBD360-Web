using System.ComponentModel.DataAnnotations;

namespace Obd360.Api.Dtos;

public record CreateScanRequest(
    [StringLength(17)] string? Vin,
    DateTime StartedAt,
    [MaxLength(200)] IReadOnlyList<string> Codes);

public record ScanRecordDto(
    Guid Id,
    string Vehicle,
    string? Vin,
    DateTime StartedAt,
    DateTime? EndedAt,
    IReadOnlyList<string> Codes);

public record PreferencesDto([Required, RegularExpression("^(metric|imperial)$")] string UnitSystem);
