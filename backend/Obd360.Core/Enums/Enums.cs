namespace Obd360.Core.Enums;

public enum UnitSystem
{
    Metric,
    Imperial
}

public enum AppTheme
{
    Light,
    Dark
}

public enum NotificationChannel
{
    None,
    Email,
    Telegram
}

public enum ConnectionType
{
    Ble
}

public enum DtcStatus
{
    Active,
    Cleared
}

public enum DtcSeverity
{
    Low,
    Medium,
    High
}

public enum ReminderStatus
{
    Pending,
    Overdue,
    Done
}

public enum ReportType
{
    WeeklyHealth
}

public enum NotificationType
{
    CriticalDtc,
    MaintenanceReminder,
    WeeklyReport
}

public enum NotificationStatus
{
    Sent,
    Failed
}

public enum AiMessageRole
{
    User,
    Assistant
}
