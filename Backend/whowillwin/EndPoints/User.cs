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
        
        // app.MapGet("/jwt", (JswTokenService jwtService) =>
        // {        
        //     return Results.Ok(jwtService.GenerateToken(
        //         userId: "user identification",
        //         email: "anna@exemple.com",
        //         issuer: "demo",
        //         role: "admin",
        //         audience: "public",    
        //         lifetime: TimeSpan.FromHours(2)));
        // }).WithTags("Users");

        //POST /users
        app.MapPost("/users", (UserRequest req, IUserRepo userRepo, ITeamRepo teamRepo) =>
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

            Result resultPass = UserValidator.ValidatePassword(userDomain);
            if (!resultPass.IsOk)
            {
                return Results.BadRequest(new
                {
                    error = resultPass.ErrorCode,
                    message = resultPass.ErrorMessage
                });
            }

            string salt = Hash.GenerateSalt();
            string hash = Hash.ComputeHash(req.Password, salt);

            UserApp userApp;
            
            try{
                userApp = req.ToUserApp(hash, salt);
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

            Team team = req.ToTeam();
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