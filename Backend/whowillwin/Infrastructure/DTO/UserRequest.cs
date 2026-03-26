using Microsoft.VisualBasic;
using whowillwin.Domain.Entities;

namespace whowillwin.DTO;

public record UserRequest(string Prefteam_id, string Name, string Email, string Password)
{
    public UserDomain ToUserDomain()
    {
        return new UserDomain
        {
            Name = Name,
            Email = Email,
            Password = Password
        };
    }

    public UserApp ToUserApp()
    {
        if (!Guid.TryParse(Prefteam_id, out Guid prefteam_id))
        {
            throw new Exception("Invalid Prefteam_id");
        }

        return new UserApp(prefteam_id, Name, Email, Password);

    }

    public Team ToTeam()
    {
        return new Team
        {
            Name = Name
        };
    }
}