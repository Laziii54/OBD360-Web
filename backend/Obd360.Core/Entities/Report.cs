using Obd360.Core.Enums;

namespace Obd360.Core.Entities;

public class Report
{
    public Guid Id { get; set; }
    public Guid VehicleId { get; set; }
    public ReportType Type { get; set; } = ReportType.WeeklyHealth;
    public DateTime GeneratedAt { get; set; } = DateTime.UtcNow;
    public string FileUrl { get; set; } = string.Empty;

    public Vehicle? Vehicle { get; set; }
}

public class NotificationLog
{
    public Guid Id { get; set; }
    public Guid UserId { get; set; }
    public NotificationChannel Channel { get; set; }
    public NotificationType Type { get; set; }
    public NotificationStatus Status { get; set; }
    public DateTime SentAt { get; set; } = DateTime.UtcNow;
}
