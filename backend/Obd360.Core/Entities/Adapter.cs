using Obd360.Core.Enums;

namespace Obd360.Core.Entities;

public class Adapter
{
    public Guid Id { get; set; }
    public Guid UserId { get; set; }
    public Guid VehicleId { get; set; }
    public string Name { get; set; } = string.Empty;
    public ConnectionType ConnectionType { get; set; } = ConnectionType.Ble;
    public DateTime? LastConnectedAt { get; set; }

    public Vehicle? Vehicle { get; set; }
}
