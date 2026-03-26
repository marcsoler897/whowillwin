using whowillwin.Domain.Entities;
using whowillwin.Common;
using whowillwin.Repository;
using whowillwin.Infrastructure.Persistence.Entities;

namespace whowillwin.Validators;

public static class UserADOValidator
{
    public static Result ValidateUserADO(UserApp userApp, UserPostgres userPostgres)
    {
        if (userPostgres.UserExists(userApp))
            return Result.Failure("Username Already Exists", "DUPLICATED USERNAME");

        return Result.Ok();
    //repetit llongitud nom validar
    }
}