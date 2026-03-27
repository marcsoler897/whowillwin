namespace whowillwin.Infrastructure.Persistence.Entities;

public class UserEntity
{
    public Guid Id { get; set; }
    public Guid Prefteam_id { get; set; }
    public string Name { get; set; }
    public string Email { get; set; }
    public string Password { get; set; }
    public string Salt { get; set; }
}