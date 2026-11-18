namespace Obd360.Api.Integrations.N8n;

/// <summary>User-facing messages for the n8n integration (Georgian, matching the rest of the UI).</summary>
public static class N8nMessages
{
    public const string NotConfigured =
        "n8n ინტეგრაცია არ არის კონფიგურირებული. მიუთითე N8n:BaseUrl appsettings-ში ან user secrets-ში.";

    public const string Unreachable =
        "n8n სერვერთან დაკავშირება ვერ მოხდა. შეამოწმე, გაშვებულია თუ არა n8n და სწორია თუ არა N8n:BaseUrl.";

    public const string Timeout =
        "n8n-მა დროზე არ უპასუხა. შეამოწმე workflow-ის მდგომარეობა და სცადე ხელახლა.";

    public const string EmptyResponse =
        "n8n-მა ცარიელი პასუხი დააბრუნა. შეამოწმე, რომ workflow-ს Respond to Webhook ნაბიჯი აქვს.";

    public const string UnreadableResponse =
        "n8n-ის პასუხი ვერ წავიკითხე. workflow-მ უნდა დააბრუნოს { \"text\": \"...\" } ფორმატის JSON.";

    public const string InvalidRequest =
        "n8n-ისთვის მოთხოვნის გაგზავნა ვერ მოხდა. სცადე ხელახლა.";

    public static string HttpError(int statusCode) =>
        $"n8n workflow-მ შეცდომა დააბრუნა (HTTP {statusCode}). შეამოწმე workflow და AI პროვაიდერის კრედენშელები.";
}
