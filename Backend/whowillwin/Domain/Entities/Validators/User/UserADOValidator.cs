using whowillwin.Domain.Entities;
using whowillwin.Common;
using whowillwin.Repository;
using whowillwin.Infrastructure.Persistence.Entities;
using whowillwin.Validators.User;

namespace whowillwin.Validators;

public static class UserADOValidator
{
    public static Result ValidateUserADO(UserApp userApp, UserPostgres userPostgres)
    {
        if (userPostgres.UserExists(userApp))
            return Result.Failure("Username Already Exists", "DUPLICATED USERNAME");

        if (userPostgres.EmailExists(userApp))
            return Result.Failure("Email Already Exists", "DUPLICATED EMAIL");

        // if (ITeamRepo.TeamExists(userApp.Prefteam_id))
        //     return Result.Failure("Email Already Exists", "DUPLICATED EMAIL");

        return Result.Ok();

    }
}