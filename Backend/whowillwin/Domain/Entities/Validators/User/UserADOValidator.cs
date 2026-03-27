using whowillwin.Domain.Entities;
using whowillwin.Common;
using whowillwin.Repository;
using whowillwin.Infrastructure.Persistence.Entities;
using whowillwin.Validators.User;

namespace whowillwin.Validators;

public static class UserADOValidator
{
    public static Result ValidateUserADO(UserApp userApp, IUserRepo userRepo, ITeamRepo teamRepo)
    {
        if (userRepo.UserExists(userApp))
            return Result.Failure("Username Already Exists", "DUPLICATED USERNAME");

        if (userRepo.EmailExists(userApp))
            return Result.Failure("Email Already Exists", "DUPLICATED EMAIL");

        if (!teamRepo.TeamExists(userApp.Prefteam_id))
            return Result.Failure("Team Doesn't Exist", "UNAVAILABLE TEAM");

        return Result.Ok();

    }
}