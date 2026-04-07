

using whowillwin.Domain.Entities;
using whowillwin.Infrastructure.Persistence.Entities;

namespace whowillwin.DTO;

public record UserResponse(Guid Id, Guid Prefteam_id, string Name, string Email) 
{
    // Guanyem CONTROL sobre com es fa la conversió

    public static UserResponse FromUser(UserEntity userEntity)   // Conversió d'entitat a response
    {
        return new UserResponse(userEntity.Id, userEntity.Prefteam_id, userEntity.Name, userEntity.Email);
    }
}
