

using whowillwin.Domain.Entities;
using whowillwin.Common;


namespace whowillwin.Validators.User;

public static class UserAppValidator
{
    public static Result ValidateTeam(UserApp userApp)
    {
        if (userApp.Prefteam_id == Guid.Empty)
        {
            return Result.Failure("Preferred Team Missing", "PREFERRED_TEAM_REQUIRED");
        }
        return Result.Ok();
    }

}
