using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;
using Obd360.Core.Entities;
using Obd360.Infrastructure.Identity;

namespace Obd360.Infrastructure.Data;

public class ApplicationDbContext : IdentityDbContext<ApplicationUser, ApplicationRole, Guid>
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) : base(options)
    {
    }

    public DbSet<UserPreference> UserPreferences => Set<UserPreference>();
    public DbSet<RefreshSession> RefreshSessions => Set<RefreshSession>();
    public DbSet<Vehicle> Vehicles => Set<Vehicle>();
    public DbSet<Adapter> Adapters => Set<Adapter>();
    public DbSet<ScanSession> ScanSessions => Set<ScanSession>();
    public DbSet<LiveReading> LiveReadings => Set<LiveReading>();
    public DbSet<DtcRecord> DtcRecords => Set<DtcRecord>();
    public DbSet<DtcCatalogEntry> DtcCatalogEntries => Set<DtcCatalogEntry>();
    public DbSet<MaintenanceReminder> MaintenanceReminders => Set<MaintenanceReminder>();
    public DbSet<AiConversation> AiConversations => Set<AiConversation>();
    public DbSet<AiMessage> AiMessages => Set<AiMessage>();
    public DbSet<Report> Reports => Set<Report>();
    public DbSet<NotificationLog> NotificationLogs => Set<NotificationLog>();

    protected override void OnModelCreating(ModelBuilder builder)
    {
        base.OnModelCreating(builder);

        builder.Entity<UserPreference>(e =>
        {
            e.HasKey(x => x.UserId);
            e.HasOne<ApplicationUser>().WithOne().HasForeignKey<UserPreference>(x => x.UserId);
        });

        builder.Entity<RefreshSession>(e =>
        {
            e.HasOne<ApplicationUser>().WithMany().HasForeignKey(x => x.UserId).OnDelete(DeleteBehavior.Cascade);
            e.HasIndex(x => x.TokenHash).IsUnique();
        });

        builder.Entity<Vehicle>(e =>
        {
            e.HasOne<ApplicationUser>().WithMany().HasForeignKey(x => x.UserId).OnDelete(DeleteBehavior.Cascade);
            e.HasIndex(x => x.UserId);
        });

        builder.Entity<Adapter>(e =>
        {
            e.HasOne<ApplicationUser>().WithMany().HasForeignKey(x => x.UserId).OnDelete(DeleteBehavior.Restrict);
            e.HasOne(x => x.Vehicle).WithOne(x => x.Adapter).HasForeignKey<Adapter>(x => x.VehicleId).OnDelete(DeleteBehavior.Cascade);
            e.HasIndex(x => x.VehicleId).IsUnique();
        });

        builder.Entity<ScanSession>(e =>
        {
            e.HasOne(x => x.Vehicle).WithMany(x => x.ScanSessions).HasForeignKey(x => x.VehicleId).OnDelete(DeleteBehavior.Cascade);
            e.HasIndex(x => new { x.VehicleId, x.StartedAt });
        });

        builder.Entity<LiveReading>(e =>
        {
            e.HasOne(x => x.Session).WithMany(x => x.LiveReadings).HasForeignKey(x => x.SessionId).OnDelete(DeleteBehavior.Cascade);
            e.Property(x => x.Value).HasColumnType("decimal(10,3)");
            e.HasIndex(x => new { x.SessionId, x.CapturedAt });
        });

        builder.Entity<DtcRecord>(e =>
        {
            e.HasOne(x => x.Session).WithMany(x => x.DtcRecords).HasForeignKey(x => x.SessionId).OnDelete(DeleteBehavior.Cascade);
            e.HasIndex(x => x.SessionId);
        });

        builder.Entity<DtcCatalogEntry>(e =>
        {
            e.HasKey(x => x.Code);
            e.Property(x => x.Category).HasMaxLength(20);
            e.Property(x => x.TitleEn).HasMaxLength(200);
            e.Property(x => x.TitleKa).HasMaxLength(200);
            e.Property(x => x.Difficulty).HasMaxLength(20);
            e.HasIndex(x => x.Category);
        });

        builder.Entity<MaintenanceReminder>(e =>
        {
            e.HasOne(x => x.Vehicle).WithMany(x => x.MaintenanceReminders).HasForeignKey(x => x.VehicleId).OnDelete(DeleteBehavior.Cascade);
            e.HasIndex(x => new { x.VehicleId, x.Status });
        });

        builder.Entity<AiConversation>(e =>
        {
            e.HasOne<ApplicationUser>().WithMany().HasForeignKey(x => x.UserId).OnDelete(DeleteBehavior.Cascade);
        });

        builder.Entity<AiMessage>(e =>
        {
            e.HasOne(x => x.Conversation).WithMany(x => x.Messages).HasForeignKey(x => x.ConversationId).OnDelete(DeleteBehavior.Cascade);
            e.HasIndex(x => new { x.ConversationId, x.CreatedAt });
        });

        builder.Entity<Report>(e =>
        {
            e.HasOne(x => x.Vehicle).WithMany(x => x.Reports).HasForeignKey(x => x.VehicleId).OnDelete(DeleteBehavior.Cascade);
            e.HasIndex(x => x.VehicleId);
        });

        builder.Entity<NotificationLog>(e =>
        {
            e.HasOne<ApplicationUser>().WithMany().HasForeignKey(x => x.UserId).OnDelete(DeleteBehavior.Cascade);
            e.HasIndex(x => new { x.UserId, x.SentAt });
        });
    }
}
