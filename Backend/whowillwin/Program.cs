using Microsoft.Extensions.Configuration;
using whowillwin.Services;
using whowillwin.Endpoints;
using Npgsql; 
using whowillwin.Common;

WebApplicationBuilder builder = WebApplication.CreateBuilder(args);

// Configuració
builder.Configuration
    .SetBasePath(AppContext.BaseDirectory)
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);

string connStr = builder.Configuration.GetConnectionString("PostgresConnection")!;
Console.WriteLine($"Postgres connection string: {connStr}");

using var conn = new Npgsql.NpgsqlConnection(connStr);
conn.Open();
Console.WriteLine("Connexió establerta!");

builder.Services.AddScoped<IDatabaseConnection>(sp =>
    new PostgresConnection(
        builder.Configuration.GetConnectionString("PostgresConnection")
    )
);


WebApplication webApp = builder.Build();

webApp.MapUserEndpoints();

webApp.Run();

