from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from db import get_connection
from elo import win_chance, HOME_ADVANTAGE

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def get_team_elo(cur, team_id: int):
    cur.execute(
        "SELECT team_name, elo FROM whowillwin.team_elo WHERE team_id = %s",
        (team_id,)
    )
    row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found. Run compute_elo.py first.")
    return row[0], row[1]  # (name, elo)


@app.get("/predict")
def predict(homeTeamId: int, awayTeamId: int):
    conn = get_connection()
    cur = conn.cursor()

    home_name, home_elo = get_team_elo(cur, homeTeamId)
    away_name, away_elo = get_team_elo(cur, awayTeamId)

    cur.close()
    conn.close()

    home_win = win_chance(home_elo + HOME_ADVANTAGE, away_elo)
    away_win = 1 - home_win

    return {
        "homeTeam":      home_name,
        "awayTeam":      away_name,
        "homeElo":       round(home_elo, 1),
        "awayElo":       round(away_elo, 1),
        "homeWinChance": round(home_win * 100, 1),
        "awayWinChance": round(away_win * 100, 1),
    }
