from db import get_connection

HOME_ADVANTAGE = 50


def get_team_elo(team_id: int) -> tuple[str, float]:
    """Fetch team name and ELO from DB. Returns (name, elo)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT team_name, elo FROM whowillwin.team_elo WHERE team_id = %s",
        (team_id,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row is None:
        raise ValueError(f"Team {team_id} not found in team_elo table")

    return row[0], row[1]  # (team_name, elo)


def win_chance(elo_a, elo_b):
    """Returns the probability (0-1) that team A wins against team B."""
    return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))


def predict(home_id: int, away_id: int):
    home_name, home_elo = get_team_elo(home_id)
    away_name, away_elo = get_team_elo(away_id)

    home_elo_effective = home_elo + HOME_ADVANTAGE

    chance_home = win_chance(home_elo_effective, away_elo)
    chance_away = 1 - chance_home

    print(f"{home_name} (ELO {home_elo}) vs {away_name} (ELO {away_elo})")
    print(f"  Home win chance : {chance_home * 100:.1f}%")
    print(f"  Away win chance : {chance_away * 100:.1f}%")


if __name__ == "__main__":
    predict(home_id=298, away_id=87)  # Girona vs Rayo Vallecano
