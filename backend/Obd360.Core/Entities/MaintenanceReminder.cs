using Obd360.Core.Enums;

namespace Obd360.Core.Entities;

public class MaintenanceReminder
{
    public Guid Id { get; set; }
    public Guid VehicleId { get; set; }
    public string Type { get; set; } = string.Empty;
    public int? DueAtKm { get; set; }
    public DateOnly? DueAtDate { get; set; }
    public ReminderStatus Status { get; set; } = ReminderStatus.Pending;

    public Vehicle? Vehicle { get; set; }
}
