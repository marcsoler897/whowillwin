using whowillwin.DTO;
// using whowillwin.Validators;
using whowillwin.Common;
using whowillwin.Domain.Entities;
using whowillwin.Repository;
using whowillwin.Infrastructure.Persistence.Entities;
using whowillwin.Infrastructure.Mappers;
// using whowillwin.Infrastructure.Persistence.Entities;
// using whowillwin.Infrastructure.Mappers;

namespace whowillwin.Endpoints;

public static class EndpointsProducts
{
    public static void MapTeamEndpoints(this WebApplication app)
    {
        app.MapPost("/teams", (TeamRequest req, TeamPostgres teamPostgres) =>
        {
        Guid id = Guid.NewGuid();

        Team team = req.ToTeam();
        TeamEntity teamEntity = TeamMapper.ToEntity(team, id);
        teamPostgres.Insert(teamEntity);

        return Results.Ok(teamEntity);
        });
    }
}