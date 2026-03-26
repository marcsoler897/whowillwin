

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

    public static Result ValidatePassword(UserApp userApp)
    {
        if (userApp.Password.Length < UserConstants.MinPasswordLength)
        {
            return Result.Failure("Password Too Short", "SHORT PASSWORD");
        }
        bool hasUpper = userApp.Password.Any(char.IsUpper);
        bool hasLower = userApp.Password.Any(char.IsLower);
        bool hasDigit = userApp.Password.Any(char.IsDigit);

        if (!hasUpper || !hasLower || !hasDigit)
        {
            return Result.Failure("Weak Password", "WEAK PASSWORD");
        }
        return Result.Ok();
    }

}
