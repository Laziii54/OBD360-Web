using System.Globalization;
using System.Text;

namespace Obd360.Api.Integrations.N8n;

/// <summary>A single diagnostic trouble code that is sent to the n8n workflow.</summary>
public sealed record ScanPromptCode(
    string Code,
    string Title,
    string Description,
    IReadOnlyList<string> Causes,
    string? Difficulty,
    bool? DiyPossible);

/// <summary>Everything the assistant knows about the latest scan.</summary>
public sealed record ScanPromptContext(
    string Vehicle,
    DateTime ScannedAt,
    IReadOnlyList<ScanPromptCode> Codes);

/// <summary>One stored conversation turn that is sent to the n8n assistant workflow.</summary>
public sealed record AiChatTurn(string Role, string Content);

/// <summary>Builds the Georgian prompts that the n8n workflows forward to the AI provider.</summary>
public static class ScanPromptBuilder
{
    private const string AssistantRules =
        "შენ ხარ OBD360-ის ავტომობილის დიაგნოსტიკის ასისტენტი.\n" +
        "უპასუხე ქართულად, მარტივი და გასაგები ენით.\n" +
        "დაეყრდენი მხოლოდ ქვემოთ მოცემულ მონაცემებს; არ მოიგონო ფაქტები, კოდები ან ნაწილების ფასები.\n" +
        "თუ ინფორმაცია არასაკმარისია, პირდაპირ თქვი, რომ მეტი დიაგნოსტიკაა საჭირო.\n" +
        "უსაფრთხოების საკითხებზე (სამუხრუჭე, აირბაგი, საჭე, საწვავის სისტემა) ურჩიე კვალიფიციურ ხელოსანს.";

    public static string BuildReportPrompt(ScanPromptContext context)
    {
        var prompt = new StringBuilder();
        prompt.AppendLine(AssistantRules);
        prompt.AppendLine();
        AppendScanContext(prompt, context);
        prompt.AppendLine();
        prompt.AppendLine("დავალება: შეადგინე მოკლე ანგარიში შემდეგი სტრუქტურით:");
        prompt.AppendLine("1. საერთო დასკვნა — არის თუ არა პრობლემა.");
        prompt.AppendLine("2. თითოეული კოდის მნიშვნელობა მარტივი ენით.");
        prompt.AppendLine("3. რამდენად სასწრაფოა და შეიძლება თუ არა მანქანის მართვა.");
        prompt.AppendLine("4. რა უნდა გააკეთოს მძღოლმა ახლა და რა — უახლოეს დროში.");
        prompt.AppendLine("5. როდის უნდა მიმართოს ხელოსანს.");
        prompt.AppendLine("პასუხი იყოს 250 სიტყვამდე და დაყავი მოკლე აბზაცებად.");

        return prompt.ToString().TrimEnd();
    }

    public static string BuildQuestionPrompt(
        ScanPromptContext? context,
        IReadOnlyList<AiChatTurn> history,
        string question)
    {
        var prompt = new StringBuilder();
        prompt.AppendLine(AssistantRules);
        prompt.AppendLine();

        if (context is null)
        {
            prompt.AppendLine("ავტომობილის მონაცემები ხელმისაწვდომი არ არის — მომხმარებელს ჯერ არ გაუკეთებია სკანირება.");
        }
        else
        {
            AppendScanContext(prompt, context);
        }

        if (history.Count > 0)
        {
            prompt.AppendLine();
            prompt.AppendLine("საუბრის ისტორია (უახლესი ბოლოს):");

            foreach (var turn in history)
            {
                var speaker = turn.Role == "assistant" ? "ასისტენტი" : "მომხმარებელი";
                prompt.AppendLine($"{speaker}: {turn.Content}");
            }
        }

        prompt.AppendLine();
        prompt.AppendLine($"მომხმარებლის კითხვა: {question}");
        prompt.AppendLine();
        prompt.AppendLine(
            "დავალება: უპასუხე მხოლოდ ამ კითხვას, წინა საუბრის კონტექსტის გათვალისწინებით. " +
            "პასუხი იყოს კონკრეტული, 200 სიტყვამდე.");

        return prompt.ToString().TrimEnd();
    }

    private static void AppendScanContext(StringBuilder prompt, ScanPromptContext context)
    {
        var scannedAt = context.ScannedAt.ToUniversalTime()
            .ToString("yyyy-MM-dd HH:mm 'UTC'", CultureInfo.InvariantCulture);

        prompt.AppendLine($"ავტომობილი: {context.Vehicle}");
        prompt.AppendLine($"სკანირების დრო: {scannedAt}");

        if (context.Codes.Count == 0)
        {
            prompt.AppendLine("ნაპოვნი კოდები: არ არის — აქტიური შეცდომის კოდები არ დაფიქსირებულა.");
            return;
        }

        prompt.AppendLine("ნაპოვნი კოდები:");

        for (var index = 0; index < context.Codes.Count; index++)
        {
            var code = context.Codes[index];
            prompt.AppendLine($"{index + 1}. {code.Code} — {code.Title}");
            prompt.AppendLine($"   აღწერა: {code.Description}");

            if (code.Causes.Count > 0)
            {
                prompt.AppendLine($"   შესაძლო მიზეზები: {string.Join("; ", code.Causes)}");
            }

            prompt.AppendLine(
                $"   სირთულე: {DescribeDifficulty(code.Difficulty)}; " +
                $"თვით შეკეთება: {DescribeDiy(code.DiyPossible)}");
        }
    }

    private static string DescribeDifficulty(string? difficulty) => difficulty?.ToLowerInvariant() switch
    {
        "easy" => "მარტივი",
        "medium" => "საშუალო",
        "hard" => "რთული",
        _ => "უცნობი"
    };

    private static string DescribeDiy(bool? diyPossible) => diyPossible switch
    {
        true => "შესაძლებელია",
        false => "არ არის რეკომენდებული",
        null => "უცნობია"
    };
}
