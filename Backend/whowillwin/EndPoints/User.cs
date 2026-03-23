// using dbdemo.Repository;
using whowillwin.Services;
using whowillwin.Model;
using whowillwin.DTO;
using System.Security.Cryptography.X509Certificates;
// using dbdemo.Validators;
using whowillwin.Common;

namespace whowillwin.Endpoints;

public static class EndpointsUsers
{
    public static void MapUserEndpoints(this WebApplication app)
    {
        //POST /users
        app.MapPost("/users", (UserRequest req, IDatabaseConnection dbConn) =>
        {
            Guid id = Guid.NewGuid();
            User user = req.ToUser(id);

            return Results.Ok(user);
        });
    }
}