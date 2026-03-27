using whowillwin.Infrastructure.Persistence.Entities;
using whowillwin.Domain.Entities;

namespace whowillwin.Infrastructure.Mappers;

public static class UserMapper
{
    public static UserEntity ToEntity(UserApp userApp, Guid id)
     => new UserEntity
     {
         Id = id,
         Prefteam_id = userApp.Prefteam_id,
         Name = userApp.Name,
         Email = userApp.Email,
         Password = userApp.Password,
         Salt = userApp.Salt
     };

    public static UserApp ToDomain(UserEntity userEntity)
        => new UserApp(
            userEntity.Prefteam_id,
            userEntity.Name,
            userEntity.Email,
            userEntity.Password,
            userEntity.Salt
        );
        
}