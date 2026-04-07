

using whowillwin.Domain.Entities;
using whowillwin.Infrastructure.Persistence.Entities;

namespace whowillwin.DTO;

public record UserJWTResponse(Guid Id, string Email, string Password, List<string> Roles)
{
    // Guanyem CONTROL sobre com es fa la conversió

    public static UserJWTResponse FromUser(Guid id, string email, string password, List<string> roles)
    {
        return new UserJWTResponse(id, email, password, roles);
    }
}
