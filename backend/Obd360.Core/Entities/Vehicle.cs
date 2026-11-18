namespace Obd360.Core.Entities;

public class Vehicle
{
    public Guid Id { get; set; }
    public Guid UserId { get; set; }
    public string? Vin { get; set; }
    public string Make { get; set; } = string.Empty;
    public string Model { get; set; } = string.Empty;
    public int Year { get; set; }
    public string? PlateNumber { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    public Adapter? Adapter { get; set; }
    public ICollection<ScanSession> ScanSessions { get; set; } = new List<ScanSession>();
    public ICollection<MaintenanceReminder> MaintenanceReminders { get; set; } = new List<MaintenanceReminder>();
    public ICollection<Report> Reports { get; set; } = new List<Report>();
}
