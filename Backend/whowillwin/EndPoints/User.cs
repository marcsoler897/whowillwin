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
using System.Security.Claims;
using Microsoft.IdentityModel.Tokens;
using whowillwin.Validators.Login;

namespace whowillwin.Endpoints;

public static class EndpointsUsers
{
    public static void MapUserEndpoints(this WebApplication app)
    {

        app.MapPost("/register", (UserRequest req, JswTokenService jwtService, IUserRepo userRepo, ITeamRepo teamRepo) =>
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

            // Guid teamId = userApp.Prefteam_id;

            // Team team = req.ToTeam();
            // TeamEntity teamEntity = TeamMapper.ToEntity(team, teamId);
            
            Guid userId = Guid.NewGuid();
            UserEntity userEntity = UserMapper.ToEntity(userApp, userId);
            userRepo.Insert(userEntity);

            string token = jwtService.GenerateToken(
                userId: userId.ToString(),
                email: userEntity.Email,
                issuer: "whowillwin",
                roles: new List<string> { "User" },
                audience: "public",
                lifetime: TimeSpan.FromHours(2)
            );

            return Results.Created($"/users/{userId}", new { token, user = UserResponse.FromUser(userEntity) });

        });
        
        app.MapPost("/login", (LoginRequest loginReq, IJWTRepo iJwtRepo, JswTokenService jwtService) =>
        {

            Result resultLogin = LoginADOValidator.ValidateLogin(loginReq, iJwtRepo);
            if (!resultLogin.IsOk)
                return Results.BadRequest(new
                {
                    error = resultLogin.ErrorCode,
                    message = resultLogin.ErrorMessage
                });

            UserJWTResponse? user = iJwtRepo.GetByLogin(loginReq.Login);

            string token = jwtService.GenerateToken(
                userId: user.Id.ToString(),
                email: user.Email,
                issuer: "whowillwin",
                roles: user.Roles,
                audience: "public",
                lifetime: TimeSpan.FromHours(2)
            );

            return Results.Ok(new { token });
        });

        // app.MapGet("/jwt", (JswTokenService jwtService) =>
        // {
        //     return Results.Ok(jwtService.GenerateToken(
        //         userId: "user identification",
        //         email: "anna@exemple.com",
        //         issuer: "demo",
        //         roles: new List<string> { "admin" },
        //         audience: "public",
        //         lifetime: TimeSpan.FromHours(2)));
        // }).WithTags("Users");

        //POST /users
        app.MapPost("/users", (ClaimsPrincipal user, UserRequest req, IUserRepo userRepo, ITeamRepo teamRepo) =>
        {


            bool isAdmin = user.Claims.Any(c =>
                c.Type == ClaimTypes.Role && c.Value == "Admin");

            if (!isAdmin)
                return Results.Forbid();

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

           Result resultPassword = UserValidator.ValidatePassword(userDomain);
           if (!resultPassword.IsOk)
            {
                return Results.BadRequest(new
                {
                    error = resultPassword.ErrorCode,
                    message = resultPassword.ErrorMessage
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
            
            Guid userId = Guid.NewGuid();
            UserEntity userEntity = UserMapper.ToEntity(userApp, userId);
            userRepo.Insert(userEntity);

            return Results.Created($"/users/{userId}", UserResponse.FromUser(userEntity));
        });

        app.MapGet("/users", (ClaimsPrincipal user, IUserRepo userRepo,int? total) =>
        {

            bool isAdmin = user.Claims.Any(c =>
                c.Type == ClaimTypes.Role && c.Value == "Admin");

            if (!isAdmin)
                return Results.Forbid();

            int limit = total ?? 20; 
            
            List<UserEntity>  users = userRepo.GetAll(limit);
            List<UserResponse> userResponse = new List<UserResponse>();
            foreach (UserEntity userEntity in users) 
            {
                UserApp userApp = UserMapper.ToDomain(userEntity);
                userResponse.Add(UserResponse.FromUser(userEntity));
            }
            
            return Results.Ok(userResponse);
        }).WithTags("Users");
    }
    public record TokenRequest(string Token);

}