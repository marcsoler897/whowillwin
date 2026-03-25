// using whowillwin.Domain.Entities;
// using whowillwin.Common;
// using whowillwin.Repository;
// using whowillwin.Infrastructure.Persistence.Entities;

// namespace SpotifyAPI.Validators;

// public static class UserADOValidator
// {
//     private static Result ValidateUserADO(UserApp userApp, TeamPostgres teamRepo)
//     {
//         if (teamRepo.TeamExists(userApp.Prefteam_id))
//             return Result.Failure("Username Already Exists", "DUPLICATED USERNAME");

//         return Result.Ok();
//     }
// }