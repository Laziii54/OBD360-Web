using System.Text.Json;

namespace Obd360.Api.Dtos;

public record DtcCatalogListItem(
    string Code,
    string Category,
    string TitleEn,
    string TitleKa,
    string Difficulty);

public record DtcCatalogDetail(
    string Code,
    string Category,
    string TitleEn,
    string TitleKa,
    string DescriptionEn,
    string DescriptionKa,
    string Difficulty,
    bool DiyPossible,
    int? EstimatedCostMin,
    int? EstimatedCostMax,
    double? EstimatedHoursMin,
    double? EstimatedHoursMax,
    JsonElement Details);

public record PagedResult<T>(IReadOnlyList<T> Items, int Total, int Page, int PageSize);
