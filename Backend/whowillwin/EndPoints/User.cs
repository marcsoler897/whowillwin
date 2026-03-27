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
        app.MapPost("/users", (UserRequest userReq, IUserRepo userRepo, ITeamRepo teamRepo) =>
        {

            UserDomain userDomain = userReq.ToUserDomain();


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
                userApp = userReq.ToUserApp();
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


            Result resultAppADO = UserADOValidator.ValidateUserADO(userApp, userRepo, teamRepo);
            if (!resultAppADO.IsOk)
            {
                return Results.BadRequest(new
                {
                    error = resultAppADO.ErrorCode,
                    message = resultAppADO.ErrorMessage
                });
            }


            Guid teamId = userApp.Prefteam_id;

            Team team = userReq.ToTeam();
            TeamEntity teamEntity = TeamMapper.ToEntity(team, teamId);


            // Result resultTeamADO = TeamADOValidator.ValidateTeamADO(teamEntity, teamRepo);
            // if (!resultTeamADO.IsOk)
            // {
            //     return Results.BadRequest(new
            //     {
            //         error = resultTeamADO.ErrorCode,
            //         message = resultTeamADO.ErrorMessage
            //     });
            // }
            
            
            Guid userId = Guid.NewGuid();

            UserEntity userEntity = UserMapper.ToEntity(userApp, userId);
            userRepo.Insert(userEntity);

            return Results.Created($"/users/{userId}", UserResponse.FromUser(userApp, userEntity));
        });

        app.MapGet("/users", (IUserRepo userRepo,int? total) =>
        {
            int limit = total ?? 20; 
            
            List<UserEntity>  users = userRepo.GetAll(limit);
            List<UserResponse> userResponse = new List<UserResponse>();
            foreach (UserEntity userEntity in users) 
            {
                UserApp userApp = UserMapper.ToDomain(userEntity);
                userResponse.Add(UserResponse.FromUser(userApp, userEntity));
            }
            
            return Results.Ok(userResponse);
        }).WithTags("Users");
    }
}