using whowillwin.Domain.Entities;
using whowillwin.Common;
using whowillwin.Repository;
using whowillwin.Infrastructure.Persistence.Entities;

namespace whowillwin.Validators;

public static class TeamADOValidator
{
    public static Result ValidateTeamADO(TeamEntity teamEntity, TeamPostgres teamPostgres)
    {
        if (!teamPostgres.TeamExists(teamEntity))
            return Result.Failure("Team Does Not Exist", "NONEXISTENT TEAM");

        return Result.Ok();
    }
}