using System.Net.Http.Headers;

namespace Obd360.Api.Integrations.N8n;

public static class N8nServiceCollectionExtensions
{
    /// <summary>Registers the n8n options and the resilient webhook client.</summary>
    public static IServiceCollection AddN8nIntegration(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        services.Configure<N8nOptions>(configuration.GetSection(N8nOptions.SectionName));

        services.AddHttpClient<IN8nClient, N8nClient>(client =>
        {
            // Per-request timeouts are enforced by N8nClient with linked cancellation tokens.
            client.Timeout = Timeout.InfiniteTimeSpan;
            client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
        });

        return services;
    }
}
