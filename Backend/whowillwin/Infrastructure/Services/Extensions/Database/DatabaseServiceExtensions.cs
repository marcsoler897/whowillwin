

namespace whowillwin.Services;
public static class DatabaseServiceExtensions
{
    public static IServiceCollection AddDatabase(
        this IServiceCollection services,
        IConfiguration config)
    {
        string providerName = config["Database:Provider"]
            ?? throw new Exception("Database provider not configured");

        if (!Enum.TryParse<DatabaseProvider>(providerName, true, out var provider))
            throw new Exception($"Unsupported database provider: {providerName}");

        switch (provider)
        {

            case DatabaseProvider.Postgres:
                services.AddScoped<IDatabaseConnection>(sp =>
                    new PostgresConnection(
                        config.GetConnectionString("Postgres")!
                    )
                );
            break;
        }

        return services;
    }
}

