using whowillwin.Common;
using whowillwin.DTO;
using whowillwin.Repository;

namespace whowillwin.Validators.Login;

public static class LoginADOValidator
{
    public static Result ValidateLogin(LoginRequest loginReq, IJWTRepo jwtRepo)
    {
        if (!jwtRepo.ValidateLogin(loginReq.Login, loginReq.Password))
            return Result.Failure("Invalid credentials", "INVALID CREDENTIALS");

        return Result.Ok();
    }
}
