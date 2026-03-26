using System.Data;
using whowillwin.Domain.Entities;
using whowillwin.Infrastructure.Persistence.Entities;
using whowillwin.Services;
using static System.Console;


namespace whowillwin.Repository;

public class UserPostgres : IUserRepo
{
    private readonly IDatabaseConnection _db;

    public UserPostgres(IDatabaseConnection db)
    {
        _db = db;
    }

    public bool UserExists(UserApp userApp)
    {
        using IDbConnection conn = _db.GetConnection();
        conn.Open();

        using IDbCommand cmd = conn.CreateCommand();
        cmd.CommandText = "SELECT COUNT(*) FROM whowillwin.users WHERE name = @name";

        var paramId = cmd.CreateParameter();
        paramId.ParameterName = "@name";
        paramId.Value = userApp.Name;
        cmd.Parameters.Add(paramId);
        
        long count = Convert.ToInt64(cmd.ExecuteScalar());;
        conn.Close();

        return count > 0;
    } 
    public void Insert(UserEntity userEntity)
    {
        using IDbConnection conn = _db.GetConnection();
        conn.Open();

        using IDbCommand cmd = conn.CreateCommand();
        cmd.CommandText = $@"INSERT INTO whowillwin.users (id, prefteam_id, name, email, password)
                            VALUES (@id, @prefteam_id, @name, @email, @password)";

        var paramId = cmd.CreateParameter();
        paramId.ParameterName = "@id";
        paramId.Value = userEntity.Id;
        cmd.Parameters.Add(paramId);

        var paramPrefteam_id = cmd.CreateParameter();
        paramPrefteam_id.ParameterName = "@prefteam_id";
        paramPrefteam_id.Value = userEntity.Prefteam_id;
        cmd.Parameters.Add(paramPrefteam_id);

        var paramName = cmd.CreateParameter();
        paramName.ParameterName = "@name";
        paramName.Value = userEntity.Name;
        cmd.Parameters.Add(paramName);

        var paramEmail = cmd.CreateParameter();
        paramEmail.ParameterName = "@email";
        paramEmail.Value = userEntity.Email;
        cmd.Parameters.Add(paramEmail);

        var paramPassword = cmd.CreateParameter();
        paramPassword.ParameterName = "@password";
        paramPassword.Value = userEntity.Password;
        cmd.Parameters.Add(paramPassword);

        int rows = cmd.ExecuteNonQuery();
        Console.WriteLine($"{rows} fila inserida.");       
    }

    public List<UserEntity> GetAll(int limit)
    {
        using IDbConnection conn = _db.GetConnection();
        conn.Open();
        string sql = $"SELECT id, prefteam_id, name, email FROM whowillwin.users LIMIT {limit}";
        
        using IDbCommand cmd = conn.CreateCommand();
        cmd.CommandText = sql;

        List<UserEntity> users = new List<UserEntity>();
        using IDataReader reader = cmd.ExecuteReader();
        while (reader.Read())
        {
            users.Add(new UserEntity
            {
                Id = reader.GetGuid(0),
                Prefteam_id = reader.GetGuid(1),
                Name = reader.GetString(2),
                Email = reader.GetString(3)
            });
        }

        return users;
    }

}
