using Obd360.Core.Enums;

namespace Obd360.Core.Entities;

public class UserPreference
{
    public Guid UserId { get; set; }
    public UnitSystem UnitSystem { get; set; } = UnitSystem.Metric;
    public AppTheme Theme { get; set; } = AppTheme.Light;
    public NotificationChannel NotificationChannel { get; set; } = NotificationChannel.None;
}

public class RefreshSession
{
    public Guid Id { get; set; }
    public Guid UserId { get; set; }
    public string TokenHash { get; set; } = string.Empty;
    public DateTime ExpiresAt { get; set; }
    public DateTime? RevokedAt { get; set; }
}
