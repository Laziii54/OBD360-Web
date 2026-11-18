namespace Obd360.Api.Dtos;

public record AiReportCode(string Code, string Title, string Description);

public record AiScanReport(
    string Vehicle,
    DateTime ScannedAt,
    bool HasProblems,
    IReadOnlyList<AiReportCode> Codes,
    string? Explanation,
    string? AiError);

public record AiAskRequest(string? Question, Guid? ConversationId);

public record AiAskResponse(
    Guid? ConversationId,
    string? Answer,
    string? Error);

public record AiConversationMessageDto(string Role, string Content, DateTime CreatedAt);

public record AiConversationDto(
    Guid Id,
    DateTime CreatedAt,
    IReadOnlyList<AiConversationMessageDto> Messages);

public record AiIntegrationStatusDto(
    bool Configured,
    bool? Reachable,
    bool ScanReportConfigured,
    bool AskConfigured,
    IReadOnlyList<string> Workflows,
    string? Message);
