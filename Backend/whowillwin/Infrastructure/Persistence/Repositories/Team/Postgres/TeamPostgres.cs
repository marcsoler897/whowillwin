using System.Data;
using whowillwin.Domain.Entities;
using whowillwin.Infrastructure.Persistence.Entities;
using whowillwin.Services;
// using whowillwin.Infrastructure.Persistence.Entities;

namespace whowillwin.Repository;

public class TeamPostgres : ITeamRepo
{
    private readonly IDatabaseConnection _db;
    public TeamPostgres(IDatabaseConnection db)
    {
        _db = db;
    }
    public bool TeamExists(UserApp userApp)
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

    public void Insert(TeamEntity teamEntity)
    {
        using IDbConnection conn = _db.GetConnection();
        conn.Open();

        using IDbCommand cmd = conn.CreateCommand();
        cmd.CommandText = $@"INSERT INTO whowillwin.teams (id, name)
                            VALUES (@id, @name)";

        var paramId = cmd.CreateParameter();
        paramId.ParameterName = "@id";
        paramId.Value = teamEntity.Id;
        cmd.Parameters.Add(paramId);

        var paramName = cmd.CreateParameter();
        paramName.ParameterName = "@name";
        paramName.Value = teamEntity.Name;
        cmd.Parameters.Add(paramName);

        int rows = cmd.ExecuteNonQuery();
        Console.WriteLine($"{rows} fila inserida.");      
    }
}