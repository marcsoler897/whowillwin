from db import get_connection

INITIAL_ELO = 1500
K = 50            # ~25 points gained/lost when beating an equal team
HOME_ADVANTAGE = 50


def win_chance(elo_a, elo_b):
    return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))


def compute_and_save():
    conn = get_connection()
    cur = conn.cursor()

    # Load all finished matches oldest first
    cur.execute("""
        SELECT home_team_id, home_team, away_team_id, away_team, home_goals, away_goals
        FROM whowillwin.matches_history
        ORDER BY utc_date ASC
    """)
    matches = cur.fetchall()
    print(f"Loaded {len(matches)} matches from history")

    elo = {}        # { team_id: elo }
    names = {}      # { team_id: team_name }
    match_count = {}  # { team_id: number of matches played }

    for home_id, home_name, away_id, away_name, home_goals, away_goals in matches:
        # Register teams on first encounter
        if home_id not in elo:
            elo[home_id] = INITIAL_ELO
            names[home_id] = home_name
            match_count[home_id] = 0
        if away_id not in elo:
            elo[away_id] = INITIAL_ELO
            names[away_id] = away_name
            match_count[away_id] = 0

        # Home team gets a virtual boost for playing at home
        expected_home = win_chance(elo[home_id] + HOME_ADVANTAGE, elo[away_id])
        expected_away = 1 - expected_home

        # Actual result: win=1, draw=0.5, loss=0
        if home_goals > away_goals:
            actual_home, actual_away = 1.0, 0.0
        elif home_goals < away_goals:
            actual_home, actual_away = 0.0, 1.0
        else:
            actual_home, actual_away = 0.5, 0.5

        # Update ELO
        elo[home_id] += K * (actual_home - expected_home)
        elo[away_id] += K * (actual_away - expected_away)

        match_count[home_id] += 1
        match_count[away_id] += 1

    # Save to team_elo table
    cur.execute("TRUNCATE whowillwin.team_elo")
    for team_id, rating in elo.items():
        cur.execute("""
            INSERT INTO whowillwin.team_elo (team_id, team_name, elo, matches)
            VALUES (%s, %s, %s, %s)
        """, (team_id, names[team_id], round(rating, 2), match_count[team_id]))

    conn.commit()
    cur.close()
    conn.close()

    # Print final rankings
    ranked = sorted(elo.items(), key=lambda x: x[1], reverse=True)
    print(f"\n{'Rank':<5} {'Team':<35} {'ELO':>7} {'Matches':>8}")
    print("-" * 58)
    for i, (team_id, rating) in enumerate(ranked, 1):
        print(f"{i:<5} {names[team_id]:<35} {rating:>7.1f} {match_count[team_id]:>8}")

    print(f"\nSaved {len(elo)} teams to team_elo table.")


if __name__ == "__main__":
    compute_and_save()
