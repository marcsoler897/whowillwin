

using whowillwin.Repository;
using whowillwin.Services;
namespace whowillwin.Extensions;

public static class TeamServicesExtensions
{
    public static IServiceCollection AddTeamServices(this IServiceCollection services,
        IConfiguration config)
    {
        string providerName = config["Database:Provider"]
            ?? throw new Exception("Database provider not configured");

        if (!Enum.TryParse<DatabaseProvider>(providerName, true, out var provider))
            throw new Exception($"Unsupported database provider: {providerName}");

        switch (provider)
        {
            case DatabaseProvider.MSSQL:
                throw new Exception($"Not implemented");
            default:
            break;

            case DatabaseProvider.Postgres:

                services.AddScoped<ITeamRepo, TeamPostgres>();
                break;
        }
        return services;
    }
}

