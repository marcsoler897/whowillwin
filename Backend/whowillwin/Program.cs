using Microsoft.Extensions.Configuration;
using whowillwin.Services;
using whowillwin.Endpoints;
using whowillwin.Repository;
using whowillwin.Extensions;
// using Microsoft.OpenApi;

/*

    dotnet add package Swashbuckle.AspNetCore

*/

WebApplicationBuilder builder = WebApplication.CreateBuilder(args);

// Configuració
builder.Configuration
    .SetBasePath(AppContext.BaseDirectory)
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);
Console.WriteLine(builder.Configuration["Database:Provider"]);
builder.Services.AddDatabase(builder.Configuration);
builder.Services.AddTeamServices(builder.Configuration);
builder.Services.AddUserServices(builder.Configuration);

builder.Services.AddEndpointsApiExplorer();

WebApplication webApp = builder.Build();

webApp.UseRouting();

Console.WriteLine($"Environment: {webApp.Environment.EnvironmentName}");

webApp.MapUserEndpoints();
webApp.MapTeamEndpoints();

webApp.Run();

