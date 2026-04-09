namespace whowillwin.Endpoints;

public static class EndpointsApiFootball
{
    private static readonly HttpClient _http = new();

    public static void MapApiFootballEndpoints(this WebApplication app)
    {
        app.MapGet("/matches", async (IConfiguration config) =>
        {
            string dateFrom = DateTime.UtcNow.ToString("yyyy-MM-dd");
            string dateTo = DateTime.UtcNow.AddDays(1).ToString("yyyy-MM-dd");

            _http.DefaultRequestHeaders.Remove("X-Auth-Token");
            _http.DefaultRequestHeaders.Add("X-Auth-Token", config["ApiFootball:AuthToken"]);

            var response = await _http.GetAsync(
                $"{config["ApiFootball:BaseUrl"]}/matches?competitions=PD&dateFrom={dateFrom}&dateTo={dateTo}"
            );

            return Results.Text(await response.Content.ReadAsStringAsync(), "application/json", statusCode: (int)response.StatusCode);
        }).WithTags("Matches");
    }
}