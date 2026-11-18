using Obd360.Core.Enums;

namespace Obd360.Core.Entities;

public class ScanSession
{
    public Guid Id { get; set; }
    public Guid VehicleId { get; set; }
    public DateTime StartedAt { get; set; } = DateTime.UtcNow;
    public DateTime? EndedAt { get; set; }
    public int? OdometerKm { get; set; }
    public ConnectionType ConnectionType { get; set; } = ConnectionType.Ble;

    public Vehicle? Vehicle { get; set; }
    public ICollection<LiveReading> LiveReadings { get; set; } = new List<LiveReading>();
    public ICollection<DtcRecord> DtcRecords { get; set; } = new List<DtcRecord>();
}

public class LiveReading
{
    public Guid Id { get; set; }
    public Guid SessionId { get; set; }
    public DateTime CapturedAt { get; set; } = DateTime.UtcNow;
    public string Pid { get; set; } = string.Empty;
    public decimal Value { get; set; }
    public string Unit { get; set; } = string.Empty;

    public ScanSession? Session { get; set; }
}

public class DtcRecord
{
    public Guid Id { get; set; }
    public Guid SessionId { get; set; }
    public string Code { get; set; } = string.Empty;
    public DtcStatus Status { get; set; } = DtcStatus.Active;
    public string? FreezeFrameJson { get; set; }

    public ScanSession? Session { get; set; }
}

public class DtcCatalogEntry
{
    public string Code { get; set; } = string.Empty;
    public string Category { get; set; } = string.Empty;
    public string TitleEn { get; set; } = string.Empty;
    public string TitleKa { get; set; } = string.Empty;
    public string DescriptionEn { get; set; } = string.Empty;
    public string DescriptionKa { get; set; } = string.Empty;
    public string Difficulty { get; set; } = "unknown";
    public bool DiyPossible { get; set; }
    public int? EstimatedCostMin { get; set; }
    public int? EstimatedCostMax { get; set; }
    public double? EstimatedHoursMin { get; set; }
    public double? EstimatedHoursMax { get; set; }
    public string DetailsJson { get; set; } = "{}";
}
