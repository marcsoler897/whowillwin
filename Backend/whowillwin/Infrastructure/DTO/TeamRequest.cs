using whowillwin.Domain.Entities;

namespace whowillwin.DTO;

public record TeamRequest(string Name)
{
    public Team ToTeam()
    {
        return new Team
        {
            Name = Name
        };
    }
}
