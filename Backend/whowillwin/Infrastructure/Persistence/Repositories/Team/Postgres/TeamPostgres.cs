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
    public void Insert(TeamEntity teamEntity)
    {
        using IDbConnection conn = _db.GetConnection();
        conn.Open();

        using IDbCommand cmd = conn.CreateCommand();
        cmd.CommandText = $@"INSERT INTO teams (Id, Name)
                            VALUES (@Id, @Name)";

        var paramId = cmd.CreateParameter();
        paramId.ParameterName = "@Id";
        paramId.Value = teamEntity.Id;
        cmd.Parameters.Add(paramId);

        var paramName = cmd.CreateParameter();
        paramName.ParameterName = "@Name";
        paramName.Value = teamEntity.Name;
        cmd.Parameters.Add(paramName);
    }
}