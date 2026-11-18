using System.Text.Json;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Obd360.Api.Dtos;
using Obd360.Api.Integrations.N8n;
using Obd360.Core.Entities;
using Obd360.Core.Enums;
using Obd360.Infrastructure.Data;

namespace Obd360.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/v1/ai")]
public class AiController : ControllerBase
{
    private const int MaxQuestionLength = 2000;
    private const int MaxHistoryMessages = 8;

    private readonly ApplicationDbContext _db;
    private readonly IN8nClient _n8n;
    private readonly ILogger<AiController> _logger;

    public AiController(ApplicationDbContext db, IN8nClient n8n, ILogger<AiController> logger)
    {
        _db = db;
        _n8n = n8n;
        _logger = logger;
    }

    /// <summary>Reports whether n8n is configured and whether the server is currently reachable.</summary>
    [HttpGet("status")]
    public async Task<ActionResult<AiIntegrationStatusDto>> Status(CancellationToken cancellationToken)
    {
        var reachable = await _n8n.ProbeAsync(cancellationToken);

        var workflows = new List<string>();
        if (_n8n.IsWorkflowConfigured(N8nWorkflow.ScanReport))
        {
            workflows.Add("scan-report");
        }

        if (_n8n.IsWorkflowConfigured(N8nWorkflow.Ask))
        {
            workflows.Add("assistant-ask");
        }

        return new AiIntegrationStatusDto(
            _n8n.IsConfigured,
            reachable,
            _n8n.IsWorkflowConfigured(N8nWorkflow.ScanReport),
            _n8n.IsWorkflowConfigured(N8nWorkflow.Ask),
            workflows,
            _n8n.IsConfigured ? null : N8nMessages.NotConfigured);
    }

    /// <summary>Builds a report for the latest scan and asks the n8n scan-report workflow to explain it.</summary>
    [HttpPost("latest-scan-report")]
    public async Task<ActionResult<AiScanReport>> LatestScanReport(CancellationToken cancellationToken)
    {
        var userId = User.GetUserId();
        var snapshot = await LoadLatestScanAsync(userId, cancellationToken);

        if (snapshot is null)
        {
            return NotFound(new { message = "სკანირება ჯერ არ არის." });
        }

        var prompt = ScanPromptBuilder.BuildReportPrompt(snapshot.Context);

        var payload = new
        {
            prompt,
            kind = "scan-report",
            locale = "ka",
            vehicle = snapshot.Context.Vehicle,
            scannedAt = snapshot.ScannedAt,
            codes = snapshot.Context.Codes
        };

        var (explanation, error) = await CallWorkflowAsync(N8nWorkflow.ScanReport, payload, cancellationToken);

        return new AiScanReport(
            snapshot.Context.Vehicle,
            snapshot.ScannedAt,
            snapshot.Context.Codes.Count > 0,
            snapshot.Context.Codes
                .Select(code => new AiReportCode(code.Code, code.Title, code.Description))
                .ToList(),
            explanation,
            error);
    }

    /// <summary>Sends a follow-up question to the n8n assistant workflow and stores the conversation.</summary>
    [HttpPost("ask")]
    public async Task<ActionResult<AiAskResponse>> Ask(
        AiAskRequest request,
        CancellationToken cancellationToken)
    {
        var question = request.Question?.Trim();
        if (string.IsNullOrWhiteSpace(question))
        {
            return BadRequest(new { message = "კითხვა ცარიელია." });
        }

        if (question.Length > MaxQuestionLength)
        {
            return BadRequest(new
            {
                message = $"კითხვა ძალიან გრძელია (მაქსიმუმ {MaxQuestionLength} სიმბოლო)."
            });
        }

        var userId = User.GetUserId();
        var conversation = await FindConversationAsync(userId, request.ConversationId, cancellationToken);

        if (request.ConversationId is { } requestedId &&
            requestedId != Guid.Empty &&
            conversation is null)
        {
            return NotFound(new { message = "საუბარი ვერ მოიძებნა." });
        }

        var history = conversation?.Messages
            .OrderBy(message => message.CreatedAt)
            .TakeLast(MaxHistoryMessages)
            .Select(message => new AiChatTurn(
                message.Role == AiMessageRole.User ? "user" : "assistant",
                message.Content))
            .ToList() ?? [];

        var snapshot = await LoadLatestScanAsync(userId, cancellationToken);
        var prompt = ScanPromptBuilder.BuildQuestionPrompt(snapshot?.Context, history, question);

        var payload = new
        {
            prompt,
            question,
            kind = "assistant-ask",
            locale = "ka",
            vehicle = snapshot?.Context.Vehicle,
            scannedAt = snapshot?.ScannedAt,
            codes = snapshot?.Context.Codes ?? [],
            history = history.Select(turn => new { role = turn.Role, content = turn.Content })
        };

        var (answer, error) = await CallWorkflowAsync(N8nWorkflow.Ask, payload, cancellationToken);
        if (answer is null)
        {
            return new AiAskResponse(conversation?.Id, null, error);
        }

        var now = DateTime.UtcNow;
        conversation ??= new AiConversation
        {
            Id = Guid.NewGuid(),
            UserId = userId,
            CreatedAt = now
        };

        // Add the messages through the DbSet explicitly: entities discovered through the
        // navigation collection of an already-tracked conversation are treated as updates.
        _db.AiMessages.AddRange(
            new AiMessage
            {
                Id = Guid.NewGuid(),
                ConversationId = conversation.Id,
                Role = AiMessageRole.User,
                Content = question,
                CreatedAt = now
            },
            new AiMessage
            {
                Id = Guid.NewGuid(),
                ConversationId = conversation.Id,
                Role = AiMessageRole.Assistant,
                Content = answer,
                CreatedAt = now.AddMilliseconds(1)
            });

        if (_db.Entry(conversation).State == EntityState.Detached)
        {
            _db.AiConversations.Add(conversation);
        }

        await _db.SaveChangesAsync(cancellationToken);

        return new AiAskResponse(conversation.Id, answer, null);
    }

    /// <summary>Returns the most recent conversation so the assistant page keeps its history after a reload.</summary>
    [HttpGet("conversation")]
    public async Task<ActionResult<AiConversationDto>> LatestConversation(CancellationToken cancellationToken)
    {
        var userId = User.GetUserId();
        var conversation = await _db.AiConversations.AsNoTracking()
            .Include(item => item.Messages)
            .Where(item => item.UserId == userId)
            .OrderByDescending(item => item.CreatedAt)
            .FirstOrDefaultAsync(cancellationToken);

        if (conversation is null)
        {
            return NoContent();
        }

        return new AiConversationDto(
            conversation.Id,
            DateTime.SpecifyKind(conversation.CreatedAt, DateTimeKind.Utc),
            conversation.Messages
                .OrderBy(message => message.CreatedAt)
                .Select(message => new AiConversationMessageDto(
                    message.Role == AiMessageRole.User ? "user" : "assistant",
                    message.Content,
                    DateTime.SpecifyKind(message.CreatedAt, DateTimeKind.Utc)))
                .ToList());
    }

    private async Task<AiConversation?> FindConversationAsync(
        Guid userId,
        Guid? conversationId,
        CancellationToken cancellationToken)
    {
        if (conversationId is not { } id || id == Guid.Empty)
        {
            return null;
        }

        return await _db.AiConversations
            .Include(conversation => conversation.Messages)
            .FirstOrDefaultAsync(
                conversation => conversation.Id == id && conversation.UserId == userId,
                cancellationToken);
    }

    private async Task<(string? Text, string? Error)> CallWorkflowAsync(
        N8nWorkflow workflow,
        object payload,
        CancellationToken cancellationToken)
    {
        if (!_n8n.IsWorkflowConfigured(workflow))
        {
            return (null, N8nMessages.NotConfigured);
        }

        var result = await _n8n.SendAsync(workflow, payload, cancellationToken);
        if (result.Success)
        {
            return (result.Text, null);
        }

        _logger.LogWarning(
            "The n8n {Workflow} workflow failed with HTTP {StatusCode}: {Error}",
            workflow,
            result.StatusCode,
            result.Error);

        return (null, result.Error ?? N8nMessages.InvalidRequest);
    }

    private async Task<ScanSnapshot?> LoadLatestScanAsync(
        Guid userId,
        CancellationToken cancellationToken)
    {
        var scan = await _db.ScanSessions.AsNoTracking()
            .Where(session => session.Vehicle!.UserId == userId)
            .OrderByDescending(session => session.StartedAt)
            .Select(session => new
            {
                session.StartedAt,
                session.Vehicle!.Model,
                Codes = session.DtcRecords.Select(record => record.Code).ToList()
            })
            .FirstOrDefaultAsync(cancellationToken);

        if (scan is null)
        {
            return null;
        }

        var entries = await _db.DtcCatalogEntries.AsNoTracking()
            .Where(entry => scan.Codes.Contains(entry.Code))
            .ToDictionaryAsync(entry => entry.Code, cancellationToken);

        var codes = scan.Codes
            .Select(code => entries.TryGetValue(code, out var entry)
                ? new ScanPromptCode(
                    code,
                    entry.TitleKa,
                    entry.DescriptionKa,
                    ReadCauses(entry.DetailsJson),
                    entry.Difficulty,
                    entry.DiyPossible)
                : new ScanPromptCode(
                    code,
                    "უცნობი კოდი",
                    "ეს კოდი კატალოგში არ არის.",
                    [],
                    null,
                    null))
            .ToList();

        var scannedAt = DateTime.SpecifyKind(scan.StartedAt, DateTimeKind.Utc);

        return new ScanSnapshot(
            new ScanPromptContext(scan.Model, scannedAt, codes),
            scannedAt);
    }

    private static IReadOnlyList<string> ReadCauses(string? detailsJson)
    {
        if (string.IsNullOrWhiteSpace(detailsJson))
        {
            return [];
        }

        try
        {
            using var details = JsonDocument.Parse(detailsJson);
            if (!details.RootElement.TryGetProperty("causes", out var causes) ||
                causes.ValueKind != JsonValueKind.Array)
            {
                return [];
            }

            return causes.EnumerateArray()
                .Select(cause => cause.TryGetProperty("ka", out var label) ? label.GetString() : null)
                .Where(label => !string.IsNullOrWhiteSpace(label))
                .Select(label => label!)
                .ToList();
        }
        catch (JsonException)
        {
            return [];
        }
    }

    private sealed record ScanSnapshot(ScanPromptContext Context, DateTime ScannedAt);
}
