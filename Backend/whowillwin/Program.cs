using Microsoft.Extensions.Configuration;
using whowillwin.Services;
using whowillwin.Endpoints;
using whowillwin.Repository;
using whowillwin.Extensions;
using whowillwin.Common;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using System.Text;
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
builder.Services.AddScoped<JswTokenService>();
builder.Services.AddTeamServices(builder.Configuration);
builder.Services.AddUserServices(builder.Configuration);


builder.Services
    .AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuerSigningKey = true,
            IssuerSigningKey =
                new SymmetricSecurityKey(
                    Encoding.UTF8.GetBytes(builder.Configuration["Jwt:JwtSecretKey"]!)
                ),

            ValidateIssuer = true,
            ValidIssuer = "demo",

            ValidateAudience = true,
            ValidAudience = "public",

            ValidateLifetime = true,
            ClockSkew = TimeSpan.FromSeconds(30)
        };
    });

builder.Services.AddAuthorization();

builder.Services.AddEndpointsApiExplorer();

WebApplication webApp = builder.Build();

webApp.UseRouting();

Console.WriteLine($"Environment: {webApp.Environment.EnvironmentName}");

// Authentication

webApp.UseAuthentication();
webApp.UseAuthorization();

// Map Endpoints

webApp.MapUserEndpoints();
webApp.MapTeamEndpoints();

webApp.Run();

