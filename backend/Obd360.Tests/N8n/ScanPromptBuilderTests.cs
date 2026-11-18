using Obd360.Api.Integrations.N8n;

namespace Obd360.Tests.N8n;

public class ScanPromptBuilderTests
{
    private static ScanPromptContext CreateContext(params ScanPromptCode[] codes) =>
        new("Toyota Camry", new DateTime(2026, 11, 11, 16, 5, 35, DateTimeKind.Utc), codes);

    [Fact]
    public void BuildReportPrompt_IncludesVehicleCodesAndCauses()
    {
        var context = CreateContext(new ScanPromptCode(
            "P0300",
            "ცილინდრის გამოტოვება",
            "ძრავი მუშაობს არასტაბილურად.",
            ["სანთლები", "კაბელები"],
            "medium",
            true));

        var prompt = ScanPromptBuilder.BuildReportPrompt(context);

        Assert.Contains("Toyota Camry", prompt);
        Assert.Contains("2026-11-11 16:05 UTC", prompt);
        Assert.Contains("P0300", prompt);
        Assert.Contains("ცილინდრის გამოტოვება", prompt);
        Assert.Contains("სანთლები; კაბელები", prompt);
        Assert.Contains("სირთულე: საშუალო", prompt);
        Assert.Contains("თვით შეკეთება: შესაძლებელია", prompt);
        Assert.Contains("დავალება:", prompt);
    }

    [Fact]
    public void BuildReportPrompt_StatesWhenNoCodesWereFound()
    {
        var prompt = ScanPromptBuilder.BuildReportPrompt(CreateContext());

        Assert.Contains("ნაპოვნი კოდები: არ არის", prompt);
    }

    [Fact]
    public void BuildReportPrompt_UnknownCodeIsDescribedAsUnknown()
    {
        var prompt = ScanPromptBuilder.BuildReportPrompt(CreateContext(new ScanPromptCode(
            "P9999",
            "უცნობი კოდი",
            "ეს კოდი კატალოგში არ არის.",
            [],
            null,
            null)));

        Assert.Contains("P9999", prompt);
        Assert.Contains("სირთულე: უცნობი", prompt);
        Assert.Contains("თვით შეკეთება: უცნობია", prompt);
    }

    [Fact]
    public void BuildQuestionPrompt_IncludesContextAndQuestion()
    {
        var context = CreateContext(new ScanPromptCode(
            "P0420",
            "კატალიზატორის ეფექტურობა",
            "კატალიზატორი ვერ ასუფთავებს გამონაბოლქვს.",
            [],
            "hard",
            false));

        var prompt = ScanPromptBuilder.BuildQuestionPrompt(context, [], "შემიძლია მანქანით მგზავრობა?");

        Assert.Contains("Toyota Camry", prompt);
        Assert.Contains("P0420", prompt);
        Assert.Contains("მომხმარებლის კითხვა: შემიძლია მანქანით მგზავრობა?", prompt);
        Assert.Contains("უპასუხე მხოლოდ ამ კითხვას", prompt);
    }

    [Fact]
    public void BuildQuestionPrompt_WorksWithoutScan()
    {
        var prompt = ScanPromptBuilder.BuildQuestionPrompt(null, [], "რა არის OBD2?");

        Assert.Contains("სკანირება", prompt);
        Assert.Contains("რა არის OBD2?", prompt);
    }

    [Fact]
    public void BuildQuestionPrompt_IncludesConversationHistory()
    {
        var history = new List<AiChatTurn>
        {
            new("user", "რას ნიშნავს P0300?"),
            new("assistant", "ეს არის წვის გამოტოვება.")
        };

        var prompt = ScanPromptBuilder.BuildQuestionPrompt(null, history, "რამდენად სასწრაფოა?");

        Assert.Contains("საუბრის ისტორია", prompt);
        Assert.Contains("მომხმარებელი: რას ნიშნავს P0300?", prompt);
        Assert.Contains("ასისტენტი: ეს არის წვის გამოტოვება.", prompt);
        Assert.Contains("მომხმარებლის კითხვა: რამდენად სასწრაფოა?", prompt);
    }
}
