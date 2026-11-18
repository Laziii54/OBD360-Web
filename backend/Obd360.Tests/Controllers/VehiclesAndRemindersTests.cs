using System.Security.Claims;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Obd360.Api.Controllers;
using Obd360.Api.Dtos;
using Obd360.Core.Entities;
using Obd360.Infrastructure.Data;

namespace Obd360.Tests.Controllers;

public class VehiclesAndRemindersTests
{
    private static ApplicationDbContext CreateDb()
    {
        var options = new DbContextOptionsBuilder<ApplicationDbContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;

        return new ApplicationDbContext(options);
    }

    private static T AsUser<T>(T controller, Guid userId) where T : ControllerBase
    {
        controller.ControllerContext = new ControllerContext
        {
            HttpContext = new DefaultHttpContext
            {
                User = new ClaimsPrincipal(
                    new ClaimsIdentity(
                        [new Claim(ClaimTypes.NameIdentifier, userId.ToString())],
                        "test"))
            }
        };

        return controller;
    }

    [Fact]
    public async Task Vehicles_List_ReturnsOnlyCurrentUserVehicles()
    {
        await using var db = CreateDb();
        var userId = Guid.NewGuid();
        var otherUserId = Guid.NewGuid();

        db.Vehicles.AddRange(
            new Vehicle
            {
                Id = Guid.NewGuid(),
                UserId = userId,
                Make = "Chevrolet",
                Model = "Volt",
                Year = 2013
            },
            new Vehicle
            {
                Id = Guid.NewGuid(),
                UserId = otherUserId,
                Make = "Toyota",
                Model = "Camry",
                Year = 2020
            });
        await db.SaveChangesAsync();

        var controller = AsUser(new VehiclesController(db), userId);

        var result = await controller.List(CancellationToken.None);

        var vehicles = Assert.IsAssignableFrom<IReadOnlyList<VehicleDto>>(result.Value);
        var vehicle = Assert.Single(vehicles);
        Assert.Equal("Chevrolet", vehicle.Make);
        Assert.Equal("Volt", vehicle.Model);
    }

    [Fact]
    public async Task Vehicles_Create_RejectsDuplicateVin()
    {
        await using var db = CreateDb();
        var userId = Guid.NewGuid();
        var controller = AsUser(new VehiclesController(db), userId);

        var request = new CreateVehicleRequest(
            "Chevrolet",
            "Volt",
            2013,
            "1G1RB6E42DU101631",
            "AA-123-BB");

        var created = await controller.Create(request, CancellationToken.None);
        var createdResult = Assert.IsType<CreatedAtActionResult>(created.Result);
        var vehicle = Assert.IsType<VehicleDto>(createdResult.Value);
        Assert.Equal("1G1RB6E42DU101631", vehicle.Vin);

        var duplicate = await controller.Create(request, CancellationToken.None);
        Assert.IsType<ConflictObjectResult>(duplicate.Result);
    }

    [Fact]
    public async Task Reminders_Create_List_Complete_Delete()
    {
        await using var db = CreateDb();
        var userId = Guid.NewGuid();

        var vehicle = new Vehicle
        {
            Id = Guid.NewGuid(),
            UserId = userId,
            Make = "Chevrolet",
            Model = "Volt",
            Year = 2013
        };
        db.Vehicles.Add(vehicle);
        await db.SaveChangesAsync();

        var controller = AsUser(new RemindersController(db), userId);

        var created = await controller.Create(
            new CreateReminderRequest(vehicle.Id, "Oil change", 125000, new DateOnly(2026, 12, 1)),
            CancellationToken.None);

        var createdResult = Assert.IsType<CreatedAtActionResult>(created.Result);
        var reminder = Assert.IsType<ReminderDto>(createdResult.Value);
        Assert.Equal("pending", reminder.Status);
        Assert.Equal("Chevrolet Volt", reminder.Vehicle);

        var list = await controller.List(null, CancellationToken.None);
        var reminders = Assert.IsAssignableFrom<IReadOnlyList<ReminderDto>>(list.Value);
        Assert.Single(reminders);

        var completed = await controller.Complete(reminder.Id, CancellationToken.None);
        Assert.IsType<NoContentResult>(completed);

        var afterComplete = await controller.List(null, CancellationToken.None);
        var completedReminder = Assert.Single(
            Assert.IsAssignableFrom<IReadOnlyList<ReminderDto>>(afterComplete.Value));
        Assert.Equal("done", completedReminder.Status);

        var deleted = await controller.Delete(reminder.Id, CancellationToken.None);
        Assert.IsType<NoContentResult>(deleted);

        var afterDelete = await controller.List(null, CancellationToken.None);
        Assert.Empty(Assert.IsAssignableFrom<IReadOnlyList<ReminderDto>>(afterDelete.Value));
    }

    [Fact]
    public async Task Reminders_CannotUseAnotherUsersVehicle()
    {
        await using var db = CreateDb();
        var ownerId = Guid.NewGuid();
        var strangerId = Guid.NewGuid();

        var vehicle = new Vehicle
        {
            Id = Guid.NewGuid(),
            UserId = ownerId,
            Make = "Chevrolet",
            Model = "Volt",
            Year = 2013
        };
        db.Vehicles.Add(vehicle);
        await db.SaveChangesAsync();

        var controller = AsUser(new RemindersController(db), strangerId);

        var result = await controller.Create(
            new CreateReminderRequest(vehicle.Id, "Oil change", null, null),
            CancellationToken.None);

        Assert.IsType<NotFoundObjectResult>(result.Result);
    }
}
