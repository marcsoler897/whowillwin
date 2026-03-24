// using whowillwin.Repository;
using whowillwin.Services;
using whowillwin.Domain.Entities;
using whowillwin.DTO;
// using System.Security.Cryptography.X509Certificates;
using whowillwin.Common;
using whowillwin.Infrastructure;
using whowillwin.Validators.User;
using Microsoft.AspNetCore.Identity;

namespace whowillwin.Endpoints;

public static class EndpointsUsers
{
    public static void MapUserEndpoints(this WebApplication app)
    {
        //POST /users
        app.MapPost("/users", (UserRequest req) =>
        {

            UserDomain userDomain = req.ToUserDomain();
            Result result = UserValidator.ValidateUser(userDomain);
            if (!result.IsOk)
            {
                return Results.BadRequest(new
                {
                    error = result.ErrorCode,
                    message = result.ErrorMessage
                });
            }


            

            UserApp userApp;
            
            try{
                userApp = req.ToUserApp();
            }
            catch(Exception ex)
            {
                return Results.BadRequest(new
                {
                    error = "INVALID TEAM",
                    message = "Invalid Team Guid"
                });
            }
                


            Result resultApp = UserAppValidator.ValidateTeam(userApp);
            if (!resultApp.IsOk)
            {
                return Results.BadRequest(new
                {
                    error = resultApp.ErrorCode,
                    message = resultApp.ErrorMessage
                });
            }
            //entity
            Guid id = Guid.NewGuid();
            // UserEntity userEntity = UserMapper

            return Results.Ok(userApp /* userresponse */);
        });
    }
}