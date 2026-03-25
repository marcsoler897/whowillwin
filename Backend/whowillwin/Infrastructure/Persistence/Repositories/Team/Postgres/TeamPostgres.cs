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
        cmd.CommandText = "SELECT COUNT(*) FROM whowillwin.teams WHERE id = @id";

        var paramId = cmd.CreateParameter();
        paramId.ParameterName = "@id";
        paramId.Value = userApp.Prefteam_id;
        cmd.Parameters.Add(paramId);
        
        int count = (int)cmd.ExecuteScalar();
        int countconvert = Convert.ToInt32(count);
        conn.Close();

        return countconvert > 0;
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