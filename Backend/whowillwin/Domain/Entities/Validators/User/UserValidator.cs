

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

    public static Result ValidatePassword(UserDomain userDomain)
    {
        if (userDomain.Password.Length < UserConstants.MinPasswordLength)
        {
            return Result.Failure("Password Too Short", "SHORT PASSWORD");
        }
        bool hasUpper = userDomain.Password.Any(char.IsUpper);
        bool hasLower = userDomain.Password.Any(char.IsLower);
        bool hasDigit = userDomain.Password.Any(char.IsDigit);

        if (!hasUpper || !hasLower || !hasDigit)
        {
            return Result.Failure("Weak Password", "WEAK PASSWORD");
        }
        return Result.Ok();
    }

}
