using Microsoft.Extensions.Configuration;
using whowillwin.Services;
using whowillwin.Endpoints;
using whowillwin.Repository;
using whowillwin.Extensions;
using whowillwin.Common;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using System.Text;
using Microsoft.AspNetCore.Identity.Data;
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
builder.Services.AddScoped<IJWTRepo, JWTPostgres>();
builder.Services.AddHttpClient();
builder.Services.AddEndpointsApiExplorer();

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
            ValidIssuer = "whowillwin",

            ValidateAudience = true,
            ValidAudience = "public",

            ValidateLifetime = true,
            ClockSkew = TimeSpan.FromSeconds(30)
        };
    });

builder.Services.AddAuthorization();

builder.Services.AddCors(options =>
{
    options.AddPolicy("frontend", policy =>
        policy.WithOrigins("http://localhost:5173")
              .AllowAnyHeader()
              .AllowAnyMethod());
});

WebApplication webApp = builder.Build();

webApp.UseRouting();
webApp.UseCors("frontend");

Console.WriteLine($"Environment: {webApp.Environment.EnvironmentName}");

// Authentication

webApp.UseAuthentication();
webApp.UseAuthorization();

// Map Endpoints

webApp.MapUserEndpoints();
webApp.MapTeamEndpoints();
webApp.MapSeasonEndpoints();
webApp.MapApiFootballEndpoints();

webApp.Run();

