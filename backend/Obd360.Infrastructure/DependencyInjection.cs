using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Obd360.Core.Interfaces;
using Obd360.Infrastructure.Data;
using Obd360.Infrastructure.Services;

namespace Obd360.Infrastructure;

public static class DependencyInjection
{
    public static IServiceCollection AddInfrastructure(this IServiceCollection services, IConfiguration configuration)
    {
        var useInMemory = configuration.GetValue<bool>("Database:UseInMemory");

        services.AddDbContext<ApplicationDbContext>(options =>
        {
            if (useInMemory)
            {
                options.UseInMemoryDatabase("Obd360Demo");
            }
            else
            {
                options.UseSqlServer(configuration.GetConnectionString("DefaultConnection"));
            }
        });

        services.Configure<JwtOptions>(configuration.GetSection("Jwt"));
        services.AddScoped<ITokenService, TokenService>();

        return services;
    }
}
