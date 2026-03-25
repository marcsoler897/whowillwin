using Microsoft.VisualBasic;
using whowillwin.Domain.Entities;

namespace whowillwin.DTO;

public record UserRequest(string Prefteam_id, string Name, string Password)
{
    public UserDomain ToUserDomain()
    {
        return new UserDomain
        {
            Name = Name,
            Password = Password
        };
    }

    public UserApp ToUserApp()
    {
        if (!Guid.TryParse(Prefteam_id, out Guid guidPrefTeam))
        {
            throw new Exception("Invalid Prefteam_id");
        }

        return new UserApp
        {
            Name = Name,
            Password = Password,
            Prefteam_id = guidPrefTeam
        };
    }

    public Team ToTeam()
    {
        return new Team
        {
            Name = Name
        };
    }
}