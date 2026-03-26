

using whowillwin.Domain.Entities;

namespace whowillwin.DTO;

public record UserResponse(Guid Prefteam_id, string Name) 
{
    // Guanyem CONTROL sobre com es fa la conversió

    public static UserResponse FromUser(UserApp userApp)   // Conversió d'entitat a response
    {
        return new UserResponse(userApp.Prefteam_id, userApp.Name);
    }
}
