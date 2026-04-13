using whowillwin.Services;
using whowillwin.DTO;
using whowillwin.Common;
using System.Data;

namespace whowillwin.Repository;

public class JWTPostgres : IJWTRepo
{

    private readonly IDatabaseConnection _db;
    public JWTPostgres(IDatabaseConnection db)
    {
        _db = db;
    }
    
    public UserJWTResponse? GetByLogin(string login)
    {

        using IDbConnection conn = _db.GetConnection();
        conn.Open();

        string sql = @"SELECT u.id, u.email, u.password, r.name
                    FROM whowillwin.users u
                    LEFT JOIN whowillwin.userroles ur ON u.id = ur.user_id
                    LEFT JOIN whowillwin.roles r ON ur.role_id = r.id
                    WHERE u.email = @Login OR u.name = @Login";

        using IDbCommand cmd = conn.CreateCommand();
        cmd.CommandText = sql;

        IDbDataParameter param = cmd.CreateParameter();
        param.ParameterName = "@Login";
        param.Value = login;
        cmd.Parameters.Add(param);

        UserJWTResponse? user = null;
        using IDataReader reader = cmd.ExecuteReader();
        List<string> roles = new List<string>();
        

        while (reader.Read())
        {
            if (user == null)
            {
                user = UserJWTResponse.FromUser(
                    reader.GetGuid(0),
                    reader.GetString(1),
                    reader.GetString(2),
                    roles
                );
            }

            if (!reader.IsDBNull(3))
                roles.Add(reader.GetString(3));
        }

        return user;
    }

    public bool ValidateLogin(string login, string password)
    {
        using IDbConnection conn = _db.GetConnection();
        conn.Open();

        using IDbCommand cmd = conn.CreateCommand();
        cmd.CommandText = "SELECT u.password, u.salt FROM whowillwin.users u WHERE u.email = @login OR u.name = @login";

        var paramLogin = cmd.CreateParameter();
        paramLogin.ParameterName = "@login";
        paramLogin.Value = login;
        cmd.Parameters.Add(paramLogin);

        using IDataReader reader = cmd.ExecuteReader();

        if (!reader.Read())
            return false;

        string storedHash = reader.GetString(0);
        string salt = reader.GetString(1);

        return Hash.ComputeHash(password, salt) == storedHash;
    }
}