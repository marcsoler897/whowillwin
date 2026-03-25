// using whowillwin.Repository;
using whowillwin.Services;
using whowillwin.Domain.Entities;
using whowillwin.DTO;
// using System.Security.Cryptography.X509Certificates;
using whowillwin.Common;
using whowillwin.Infrastructure;
using whowillwin.Validators.User;
using Microsoft.AspNetCore.Identity;
using whowillwin.Validators;
using whowillwin.Repository;
using whowillwin.Infrastructure.Mappers;
using whowillwin.Infrastructure.Persistence.Entities;

namespace whowillwin.Endpoints;

public static class EndpointsUsers
{
    public static void MapUserEndpoints(this WebApplication app)
    {
        //POST /users
        app.MapPost("/users", (UserRequest req, UserPostgres userPostgres) =>
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
            catch(Exception)
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

            // Result resultAppADO = UserADOValidator.ValidateUserADO(userApp, teamPostgres);
            // if (!resultAppADO.IsOk)
            // {
            //     return Results.BadRequest(new
            //     {
            //         error = resultAppADO.ErrorCode,
            //         message = resultAppADO.ErrorMessage
            //     });
            // }
            //entity
            Guid id = Guid.NewGuid();

            UserEntity userEntity = UserMapper.ToEntity(userApp, id);
            userPostgres.Insert(userEntity);

            return Results.Ok(userApp /* userresponse */);
        });
    }
}