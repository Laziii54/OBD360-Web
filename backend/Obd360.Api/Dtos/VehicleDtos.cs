using System.ComponentModel.DataAnnotations;

namespace Obd360.Api.Dtos;

public record VehicleDto(
    Guid Id,
    string? Vin,
    string Make,
    string Model,
    int Year,
    string? PlateNumber,
    int ScanCount,
    DateTime? LastScanAt,
    DateTime CreatedAt);

public record CreateVehicleRequest(
    [Required, StringLength(60, MinimumLength = 1)] string Make,
    [Required, StringLength(60, MinimumLength = 1)] string Model,
    [Range(1900, 2100)] int Year,
    [RegularExpression("^$|^[A-HJ-NPR-Z0-9]{17}$", ErrorMessage = "VIN უნდა შედგებოდეს 17 სიმბოლოსგან.")]
    string? Vin,
    [StringLength(20)] string? PlateNumber);

public record UpdateVehicleRequest(
    [Required, StringLength(60, MinimumLength = 1)] string Make,
    [Required, StringLength(60, MinimumLength = 1)] string Model,
    [Range(1900, 2100)] int Year,
    [RegularExpression("^$|^[A-HJ-NPR-Z0-9]{17}$", ErrorMessage = "VIN უნდა შედგებოდეს 17 სიმბოლოსგან.")]
    string? Vin,
    [StringLength(20)] string? PlateNumber);
