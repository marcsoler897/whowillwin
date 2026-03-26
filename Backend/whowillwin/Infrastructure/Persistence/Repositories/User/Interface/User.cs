// using whowillwin.Infrastructure.Persistence.Entities;

using whowillwin.Domain.Entities;
using whowillwin.Infrastructure.Persistence.Entities;

namespace whowillwin.Repository;

public interface IUserRepo
{
    List<ProductEntity> GetAll(int limit);
    void Insert(UserEntity userEntity);
}
