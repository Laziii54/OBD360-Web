namespace Obd360.Api.Dtos;

public record AdminOverviewDto(
    int Users,
    int Vehicles,
    int Scans,
    int DtcCodes);

public record AdminUserDto(
    Guid Id,
    string DisplayName,
    string Email,
    IReadOnlyList<string> Roles,
    int Vehicles,
    int Scans,
    DateTime JoinedAt);

public record AdminScanDto(
    Guid Id,
    DateTime ScannedAt,
    string User,
    string Vehicle,
    string? Vin,
    IReadOnlyList<string> Codes,
    string Status);
