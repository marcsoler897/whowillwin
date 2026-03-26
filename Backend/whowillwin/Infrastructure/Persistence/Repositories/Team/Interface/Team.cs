// using whowillwin.Infrastructure.Persistence.Entities;

using whowillwin.Domain.Entities;
using whowillwin.Infrastructure.Persistence.Entities;

namespace whowillwin.Repository;

public interface ITeamRepo
{
    bool TeamExists(Guid Id);
    void Insert(TeamEntity teamEntity);
}
