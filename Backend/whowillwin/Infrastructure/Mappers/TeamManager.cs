using whowillwin.Infrastructure.Persistence.Entities;
using whowillwin.Domain.Entities;

namespace whowillwin.Infrastructure.Mappers;

public static class TeamMapper
{
    public static TeamEntity ToEntity(Team team, Guid id)
     => new TeamEntity
     {
         Id = id,
         Name = team.Name
     };
}