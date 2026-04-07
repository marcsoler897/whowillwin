// using whowillwin.Infrastructure.Persistence.Entities;

using whowillwin.Domain.Entities;
using whowillwin.Infrastructure.Persistence.Entities;

namespace whowillwin.Repository;

public interface IUserRepo
{
    bool UserExists(UserApp userApp);
    bool EmailExists(UserApp userApp);
    List<UserEntity> GetAll(int limit);
    void Insert(UserEntity userEntity);
    

}
