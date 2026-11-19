using Microsoft.EntityFrameworkCore;
using Obd360.Core.Entities;
using Obd360.Core.Enums;
using Obd360.Core.Interfaces;
using Obd360.Infrastructure.Data;

namespace Obd360.Api.Services;

/// <summary>
/// Once per configured interval, emails a digest of due maintenance reminders.
/// NotificationLogs prevents sending the same user more than one email per day.
/// </summary>
public sealed class ReminderNotificationService : BackgroundService
{
    private readonly IServiceScopeFactory _scopeFactory;
    private readonly IConfiguration _configuration;
    private readonly ILogger<ReminderNotificationService> _logger;

    public ReminderNotificationService(
        IServiceScopeFactory scopeFactory,
        IConfiguration configuration,
        ILogger<ReminderNotificationService> logger)
    {
        _scopeFactory = scopeFactory;
        _configuration = configuration;
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        if (!_configuration.GetValue("Reminders:Enabled", true))
        {
            _logger.LogInformation("Reminder email notifications are disabled.");
            return;
        }

        var minutes = Math.Max(1, _configuration.GetValue("Reminders:CheckIntervalMinutes", 360));

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await SendDueRemindersAsync(stoppingToken);
            }
            catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested)
            {
                break;
            }
            catch (Exception exception)
            {
                _logger.LogError(exception, "Reminder notification check failed.");
            }

            try
            {
                await Task.Delay(TimeSpan.FromMinutes(minutes), stoppingToken);
            }
            catch (OperationCanceledException)
            {
                break;
            }
        }
    }

    private async Task SendDueRemindersAsync(CancellationToken cancellationToken)
    {
        using var scope = _scopeFactory.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
        var emailSender = scope.ServiceProvider.GetRequiredService<IEmailSender>();

        var today = DateOnly.FromDateTime(DateTime.UtcNow);
        var startOfDay = DateTime.UtcNow.Date;

        var due = await (
                from reminder in db.MaintenanceReminders.AsNoTracking()
                join vehicle in db.Vehicles.AsNoTracking() on reminder.VehicleId equals vehicle.Id
                join user in db.Users.AsNoTracking() on vehicle.UserId equals user.Id
                where reminder.Status != ReminderStatus.Done
                      && reminder.DueAtDate != null
                      && reminder.DueAtDate <= today
                      && user.Email != null
                select new
                {
                    UserId = user.Id,
                    Email = user.Email!,
                    user.DisplayName,
                    reminder.Type,
                    DueAtDate = reminder.DueAtDate!.Value
                })
            .ToListAsync(cancellationToken);

        if (due.Count == 0)
        {
            return;
        }

        foreach (var group in due.GroupBy(item => item.UserId))
        {
            var alreadySent = await db.NotificationLogs.AsNoTracking().AnyAsync(
                log => log.UserId == group.Key
                       && log.Type == NotificationType.MaintenanceReminder
                       && log.Channel == NotificationChannel.Email
                       && log.Status == NotificationStatus.Sent
                       && log.SentAt >= startOfDay,
                cancellationToken);

            if (alreadySent)
            {
                continue;
            }

            var first = group.First();
            var reminders = group
                .Select(item => $"{item.Type} — {item.DueAtDate:dd.MM.yyyy}")
                .Distinct()
                .ToList();

            var sent = false;

            try
            {
                sent = await emailSender.SendReminderEmailAsync(
                    first.Email,
                    first.DisplayName,
                    reminders,
                    cancellationToken);
            }
            catch (OperationCanceledException) when (cancellationToken.IsCancellationRequested)
            {
                throw;
            }
            catch (Exception exception)
            {
                _logger.LogWarning(
                    exception,
                    "Could not send reminder email to {Email}.",
                    first.Email);
            }

            db.NotificationLogs.Add(new NotificationLog
            {
                Id = Guid.NewGuid(),
                UserId = group.Key,
                Channel = NotificationChannel.Email,
                Type = NotificationType.MaintenanceReminder,
                Status = sent ? NotificationStatus.Sent : NotificationStatus.Failed,
                SentAt = DateTime.UtcNow
            });

            await db.SaveChangesAsync(cancellationToken);
        }
    }
}
