namespace whowillwin.Endpoints;

public static class EndpointsApiFootball
{
    public static void MapApiFootballEndpoints(this WebApplication app)
    {
        app.MapGet("/competitions/{id}/seasons", async (int id, IHttpClientFactory factory, IConfiguration config) =>
        {
            var http = factory.CreateClient();
            http.DefaultRequestHeaders.Add("X-Auth-Token", config["ApiFootball:AuthToken"]);

            var response = await http.GetAsync($"{config["ApiFootball:BaseUrl"]}/competitions/{id}");

            return Results.Text(await response.Content.ReadAsStringAsync(), "application/json", statusCode: (int)response.StatusCode);
        }).WithTags("Matches");

        app.MapGet("/teams/{id}", async (int id, IHttpClientFactory factory, IConfiguration config) =>
        {
            var http = factory.CreateClient();
            http.DefaultRequestHeaders.Add("X-Auth-Token", config["ApiFootball:AuthToken"]);

            var response = await http.GetAsync($"{config["ApiFootball:BaseUrl"]}/teams/{id}");

            return Results.Text(await response.Content.ReadAsStringAsync(), "application/json", statusCode: (int)response.StatusCode);
        }).WithTags("Matches");

        app.MapGet("/competitions/{id}/matches", async (int id, int season, IHttpClientFactory factory, IConfiguration config) =>
        {
            var http = factory.CreateClient();
            http.DefaultRequestHeaders.Add("X-Auth-Token", config["ApiFootball:AuthToken"]);

            var response = await http.GetAsync($"{config["ApiFootball:BaseUrl"]}/competitions/{id}/matches?season={season}");

            return Results.Text(await response.Content.ReadAsStringAsync(), "application/json", statusCode: (int)response.StatusCode);
        }).WithTags("Matches");
    }
}
