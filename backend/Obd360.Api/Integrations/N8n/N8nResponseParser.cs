using System.Text.Json;

namespace Obd360.Api.Integrations.N8n;

/// <summary>
/// Pulls the answer text out of the many response shapes an n8n workflow can return:
/// {"text":"..."}, {"output":"..."}, an array of items, an Anthropic message, an OpenAI chat completion, or plain text.
/// </summary>
public static class N8nResponseParser
{
    private const int MaxDepth = 8;

    private static readonly string[] TextPropertyNames =
    [
        "text",
        "answer",
        "output",
        "explanation",
        "response",
        "result",
        "choices",
        "content",
        "data",
        "body",
        "payload",
        "message"
    ];

    public static string? ExtractText(string? body)
    {
        if (string.IsNullOrWhiteSpace(body))
        {
            return null;
        }

        var trimmed = body.Trim();
        if (trimmed[0] is not ('{' or '[' or '"'))
        {
            return trimmed;
        }

        try
        {
            using var document = JsonDocument.Parse(trimmed);
            return ExtractText(document.RootElement, 0);
        }
        catch (JsonException)
        {
            // The body looked like JSON but was not valid; treat it as an unreadable response.
            return null;
        }
    }

    private static string? ExtractText(JsonElement element, int depth)
    {
        if (depth > MaxDepth)
        {
            return null;
        }

        switch (element.ValueKind)
        {
            case JsonValueKind.String:
                var value = element.GetString();
                return string.IsNullOrWhiteSpace(value) ? null : value.Trim();

            case JsonValueKind.Array:
                foreach (var item in element.EnumerateArray())
                {
                    var text = ExtractText(item, depth + 1);
                    if (text is not null)
                    {
                        return text;
                    }
                }

                return null;

            case JsonValueKind.Object:
                foreach (var propertyName in TextPropertyNames)
                {
                    if (element.TryGetProperty(propertyName, out var property))
                    {
                        var text = ExtractText(property, depth + 1);
                        if (text is not null)
                        {
                            return text;
                        }
                    }
                }

                return null;

            default:
                return null;
        }
    }
}
