namespace whowillwin.Model;

public class User
{
    public Guid Id { get; set; }
    public Guid Prefteam_id { get; set; }
    public string Name { get; set; }
    public string Password { get; set; }
}