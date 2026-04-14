import requests
from db import get_connection

API_TOKEN = "dfa2c7aa37eb4a7e893d6bf5b25018a1"
BASE_URL = "https://api.football-data.org/v4"
COMPETITION_ID = 2014
SEASONS = [2023, 2024]  # only seasons with data on free tier

def fetch_and_store():
    conn = get_connection()
    cur = conn.cursor()
    total = 0

    for season in SEASONS:
        print(f"Fetching season {season}...", end=" ", flush=True)
        resp = requests.get(
            f"{BASE_URL}/competitions/{COMPETITION_ID}/matches",
            headers={"X-Auth-Token": API_TOKEN},
            params={"season": season},
        )
        if not resp.ok:
            print(f"error {resp.status_code}, skipping.")
            continue

        matches = resp.json().get("matches", [])
        inserted = 0

        for m in matches:
            if m["status"] != "FINISHED":
                continue
            season_year = int(m["season"]["startDate"][:4])
            cur.execute(
                """
                INSERT INTO whowillwin.matches_history
                    (id, season, matchday, utc_date, home_team_id, home_team,
                     away_team_id, away_team, home_goals, away_goals)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    m["id"],
                    season_year,
                    m.get("matchday"),
                    m["utcDate"],
                    m["homeTeam"]["id"],
                    m["homeTeam"]["name"],
                    m["awayTeam"]["id"],
                    m["awayTeam"]["name"],
                    m["score"]["fullTime"]["home"],
                    m["score"]["fullTime"]["away"],
                ),
            )
            inserted += cur.rowcount

        conn.commit()
        total += inserted
        print(f"{inserted} matches inserted.")

    cur.close()
    conn.close()
    print(f"\nAll done. {total} total new matches inserted.")

if __name__ == "__main__":
    fetch_and_store()
