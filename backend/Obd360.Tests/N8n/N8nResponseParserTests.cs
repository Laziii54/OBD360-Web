using Obd360.Api.Integrations.N8n;

namespace Obd360.Tests.N8n;

public class N8nResponseParserTests
{
    [Fact]
    public void ExtractText_ReadsFlatTextObject()
    {
        var text = N8nResponseParser.ExtractText("""{"text":"გამარჯობა","model":"claude"}""");

        Assert.Equal("გამარჯობა", text);
    }

    [Fact]
    public void ExtractText_ReadsAnthropicMessage()
    {
        var body = """
        {
          "id": "msg_1",
          "content": [
            { "type": "text", "text": "პირველი ნაწილი" },
            { "type": "text", "text": "მეორე ნაწილი" }
          ]
        }
        """;

        Assert.Equal("პირველი ნაწილი", N8nResponseParser.ExtractText(body));
    }

    [Fact]
    public void ExtractText_ReadsOpenAiChatCompletion()
    {
        var body = """
        {
          "choices": [
            { "message": { "role": "assistant", "content": "OpenAI პასუხი" } }
          ]
        }
        """;

        Assert.Equal("OpenAI პასუხი", N8nResponseParser.ExtractText(body));
    }

    [Fact]
    public void ExtractText_ReadsFirstItemOfArray()
    {
        var body = """[{"output":"პასუხი მასივიდან"}]""";

        Assert.Equal("პასუხი მასივიდან", N8nResponseParser.ExtractText(body));
    }

    [Fact]
    public void ExtractText_ReturnsPlainTextAsIs()
    {
        Assert.Equal("უბრალო ტექსტი", N8nResponseParser.ExtractText("  უბრალო ტექსტი  "));
    }

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    [InlineData("{}")]
    [InlineData("""{"status":"ok"}""")]
    [InlineData("{not-json")]
    public void ExtractText_ReturnsNull_WhenThereIsNoAnswer(string body)
    {
        Assert.Null(N8nResponseParser.ExtractText(body));
    }
}
