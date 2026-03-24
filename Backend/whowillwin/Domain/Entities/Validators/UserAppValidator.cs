

using whowillwin.Domain.Entities;
using whowillwin.Common;


namespace whowillwin.Validators;

public static class UserAppValidator
{
    public static Result ValidateTeam(UserApp userApp)
    {
        if (userApp.Prefteam_id == null || userApp.Prefteam_id.Count() == 0 )
        {
            return Result.Failure("Preferred Team Missing", "PREFERRED_TEAM_REQUIRED");
        }
        return Result.Ok();
    }

}
