using System.Text.Json;
using System.Text.RegularExpressions;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Obd360.Api.Dtos;
using Obd360.Infrastructure.Data;

namespace Obd360.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/v1/dtc-catalog")]
public partial class DtcCatalogController : ControllerBase
{
    private const int MaxPageSize = 100;

    // Reserved ISO/SAE placeholders stay out of browsing, but an exact code search finds them.
    private const string ReservedDifficulty = "unknown";

    private readonly ApplicationDbContext _db;

    public DtcCatalogController(ApplicationDbContext db)
    {
        _db = db;
    }

    [HttpGet]
    public async Task<ActionResult<PagedResult<DtcCatalogListItem>>> List(
        [FromQuery] string? search,
        [FromQuery] string? category,
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 25)
    {
        page = Math.Max(page, 1);
        pageSize = Math.Clamp(pageSize, 1, MaxPageSize);

        var term = search?.Trim();
        var query = _db.DtcCatalogEntries.AsNoTracking();

        if (string.IsNullOrEmpty(term) || !ExactCode().IsMatch(term))
        {
            query = query.Where(e => e.Difficulty != ReservedDifficulty);
        }

        if (!string.IsNullOrWhiteSpace(category))
        {
            query = query.Where(e => e.Category == category);
        }

        if (!string.IsNullOrEmpty(term))
        {
            query = query.Where(e =>
                e.Code.Contains(term) ||
                e.TitleEn.Contains(term) ||
                e.TitleKa.Contains(term) ||
                e.DescriptionEn.Contains(term) ||
                e.DescriptionKa.Contains(term));
        }

        var total = await query.CountAsync();
        var items = await query
            .OrderBy(e => e.Code)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .Select(e => new DtcCatalogListItem(e.Code, e.Category, e.TitleEn, e.TitleKa, e.Difficulty))
            .ToListAsync();

        return new PagedResult<DtcCatalogListItem>(items, total, page, pageSize);
    }

    [HttpGet("{code}")]
    public async Task<ActionResult<DtcCatalogDetail>> Get(string code)
    {
        var normalizedCode = code.ToUpperInvariant();
        var entry = await _db.DtcCatalogEntries.AsNoTracking()
            .FirstOrDefaultAsync(e => e.Code == normalizedCode);

        if (entry is null)
        {
            return NotFound();
        }

        using var details = JsonDocument.Parse(entry.DetailsJson);

        return new DtcCatalogDetail(
            entry.Code,
            entry.Category,
            entry.TitleEn,
            entry.TitleKa,
            entry.DescriptionEn,
            entry.DescriptionKa,
            entry.Difficulty,
            entry.DiyPossible,
            entry.EstimatedCostMin,
            entry.EstimatedCostMax,
            entry.EstimatedHoursMin,
            entry.EstimatedHoursMax,
            details.RootElement.Clone());
    }

    [GeneratedRegex("^[PCBU][0-9A-Fa-f]{4}$", RegexOptions.IgnoreCase)]
    private static partial Regex ExactCode();
}
