using System.Data;

namespace whowillwin.Services;

public interface IDatabaseConnection {
    IDbConnection GetConnection();

}
