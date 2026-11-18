using System.IO.Compression;
using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using Obd360.Core.Entities;
using Obd360.Infrastructure.Data;

namespace Obd360.Infrastructure.Services;

public static class DtcCatalogSeeder
{
    /// <summary>Imports the catalog into an empty table and returns the number of imported rows.</summary>
    public static async Task<int> SeedAsync(ApplicationDbContext db, string filePath)
    {
        if (await db.DtcCatalogEntries.AnyAsync())
        {
            return 0;
        }

        await using var file = File.OpenRead(filePath);
        await using var gzip = new GZipStream(file, CompressionMode.Decompress);
        var entries = await JsonSerializer.DeserializeAsync<List<DtcCatalogEntry>>(
            gzip, new JsonSerializerOptions(JsonSerializerDefaults.Web)) ?? [];

        db.ChangeTracker.AutoDetectChangesEnabled = false;
        db.DtcCatalogEntries.AddRange(entries);
        await db.SaveChangesAsync();
        db.ChangeTracker.AutoDetectChangesEnabled = true;
        db.ChangeTracker.Clear();

        return entries.Count;
    }
}
