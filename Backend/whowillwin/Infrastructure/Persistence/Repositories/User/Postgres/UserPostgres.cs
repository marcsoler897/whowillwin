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



    // public List<TeamEntity> GetAll(int limit)
    // {
    //     using IDbConnection conn = _db.GetConnection();
    //     conn.Open();
    //     string sql = "SELECT COUNT(*) FROM teams WHERE id = @id";
        
    //     using IDbCommand cmd = conn.CreateCommand();
    //     cmd.CommandText = sql;

    //     List<TeamEntity> products = new List<TeamEntity>();
    //     using IDataReader reader = cmd.ExecuteReader();
    //     while (reader.Read())
    //     {
    //         products.Add(new TeamEntity
    //         {
    //             Id = reader.GetGuid(0),
    //              = reader.GetString(1),
    //             Name = reader.GetString(2),
    //             Price = reader.GetDecimal(3)
    //         });
    //     }

    //     return products;
    // }
    public void Insert(UserEntity userEntity)
    {
        using IDbConnection conn = _db.GetConnection();
        conn.Open();

        using IDbCommand cmd = conn.CreateCommand();
        cmd.CommandText = $@"INSERT INTO users (id, prefteam_id, name, password)
                            VALUES (@id, @prefteam_id, @name, @password)";

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

        var paramPassword = cmd.CreateParameter();
        paramPassword.ParameterName = "@password";
        paramPassword.Value = userEntity.Password;
        cmd.Parameters.Add(paramPassword);

        int rows = cmd.ExecuteNonQuery();
        Console.WriteLine($"{rows} fila inserida.");       
    }
}
