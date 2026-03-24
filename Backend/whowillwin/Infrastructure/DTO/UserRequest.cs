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
        return new UserApp
        {
            Name = Name,
            Password = Password,
            Prefteam_id = Prefteam_id
        };
    }
}