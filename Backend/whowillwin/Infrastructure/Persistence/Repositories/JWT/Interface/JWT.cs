// using whowillwin.Infrastructure.Persistence.Entities;

using whowillwin.Domain.Entities;
using whowillwin.DTO;  
using whowillwin.Infrastructure.Persistence.Entities;

namespace whowillwin.Repository;

public interface IJWTRepo
{
    UserJWTResponse? GetByLogin(string login);
}
