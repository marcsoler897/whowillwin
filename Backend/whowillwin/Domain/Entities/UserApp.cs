namespace whowillwin.Domain.Entities;

public class UserApp
{
    public Guid Prefteam_id { get; set; }
    public string Name { get; set; }
    public string Email { get; set; }
    public string Password { get; set; }
    public string Salt { get; set; }

    public UserApp(Guid prefteam_id, string name, string email, string password, string salt)
    {
        Prefteam_id=prefteam_id;
        Name=name;
        Email=email;
        Password=password;
        Salt=salt;
    }

}