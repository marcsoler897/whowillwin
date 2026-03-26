

using whowillwin.Domain.Entities;
using whowillwin.Common;
using whowillwin.Infrastructure.Persistence.Entities;
using whowillwin.Repository;


namespace whowillwin.Validators.User;

public static class UserValidator
{
    public static Result ValidateUser(UserDomain userDomain)
    {
        if (userDomain.Name == null || userDomain.Name.Count() == 0 )
        {
            return Result.Failure("Username Required","INCORRECT USERNAME");
        }
        if (!userDomain.Name.All(char.IsLetter))
        {
            return Result.Failure("Username Only Letters", "INCORRECT USERNAME");
        }
        // if (userDomain.Name.Count() > UserConstants.MaxUsernameLength )
        // {
        //     return Result.Failure("Max Username Length 32","INCORRECT USERNAME");
        // }
        if (string.IsNullOrEmpty(userDomain.Password))
        {
            return Result.Failure("Password Required","INCORRECT PASSWORD");
        }

        if (string.IsNullOrEmpty(userDomain.Email))
        {
            return Result.Failure("Email is Required", "EMAIL REQUIRED");
        }
        return Result.Ok();

    }

}
