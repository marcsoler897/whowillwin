

using System.Data;
using Npgsql;

namespace whowillwin.Services;

public class PostgresConnection : IDatabaseConnection
{
    private readonly string _connectionString;
    
    public PostgresConnection(string connectionString)
    {
        _connectionString = connectionString;
    }

    // Retorna una nova connexió Npgsql cada cop
    public IDbConnection GetConnection()
    {
        return new NpgsqlConnection(_connectionString);
    }
}


