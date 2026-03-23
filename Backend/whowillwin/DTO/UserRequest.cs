using whowillwin.Model;

namespace whowillwin.DTO;

public record UserRequest(string Name, string Password)
{
    public User ToUser(Guid id)
    {
        return new User
        {
            Id = id,
            // Prefteam_id = Prefteam_id,
            Name = Name,
            Password = Password
        };
    }
}