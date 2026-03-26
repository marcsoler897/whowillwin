// using whowillwin.Infrastructure.Persistence.Entities;

using whowillwin.Domain.Entities;
using whowillwin.Infrastructure.Persistence.Entities;

namespace whowillwin.Repository;

public interface IUserRepo
{
    List<UserEntity> GetAll(int limit);
    void Insert(UserEntity userEntity);
}
