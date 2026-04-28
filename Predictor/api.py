import pandas as pd
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestClassifier
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres")

# ── build rolling features ────────────────────────────────────────────────────

df = pd.read_sql("""
    SELECT
        m.season, m.matchday, m.utc_date,
        m.home_team_id, m.away_team_id,
        ht.api_id AS home_api_id,
        at.api_id AS away_api_id,
        m.home_goals, m.away_goals, m.winner
    FROM whowillwin.matches m
    JOIN whowillwin.teams ht ON ht.id = m.home_team_id
    JOIN whowillwin.teams at ON at.id = m.away_team_id
""", engine)
df = df[[
    "season", "matchday", "utc_date",
    "home_team_id", "away_team_id",
    "home_api_id", "away_api_id",
    "home_goals", "away_goals", "winner",
]]
df = df.sort_values("utc_date").reset_index(drop=True)

team_stats: dict = {}

home_avg_goals, away_avg_goals = [], []
home_avg_conceded, away_avg_conceded = [], []
home_win_rate, away_win_rate = [], []

def safe_mean(lst):
    return float(sum(lst) / len(lst)) if lst else 0.0

for _, row in df.iterrows():
    home = row["home_team_id"]
    away = row["away_team_id"]

    for t in (home, away):
        if t not in team_stats:
            team_stats[t] = {"scored": [], "conceded": [], "wins": []}

    home_avg_goals.append(safe_mean(team_stats[home]["scored"]))
    away_avg_goals.append(safe_mean(team_stats[away]["scored"]))
    home_avg_conceded.append(safe_mean(team_stats[home]["conceded"]))
    away_avg_conceded.append(safe_mean(team_stats[away]["conceded"]))
    home_win_rate.append(safe_mean(team_stats[home]["wins"]))
    away_win_rate.append(safe_mean(team_stats[away]["wins"]))

    hg, ag = row["home_goals"], row["away_goals"]
    if not pd.isna(hg) and not pd.isna(ag):
        team_stats[home]["scored"].append(hg)
        team_stats[home]["conceded"].append(ag)
        team_stats[away]["scored"].append(ag)
        team_stats[away]["conceded"].append(hg)
        if hg > ag:
            team_stats[home]["wins"].append(1); team_stats[away]["wins"].append(0)
        elif hg < ag:
            team_stats[home]["wins"].append(0); team_stats[away]["wins"].append(1)
        else:
            team_stats[home]["wins"].append(0); team_stats[away]["wins"].append(0)

df["home_avg_goals"]    = home_avg_goals
df["away_avg_goals"]    = away_avg_goals
df["home_avg_conceded"] = home_avg_conceded
df["away_avg_conceded"] = away_avg_conceded
df["home_win_rate"]     = home_win_rate
df["away_win_rate"]     = away_win_rate

# ── train model ───────────────────────────────────────────────────────────────

FEATURES = [
    "matchday",
    "home_avg_goals", "away_avg_goals",
    "home_avg_conceded", "away_avg_conceded",
    "home_win_rate", "away_win_rate",
]

df_train  = df[df["winner"].notna()].copy()
df_future = df[df["winner"].isna()].copy()

model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(df_train[FEATURES], df_train["winner"])

classes = list(model.classes_)
home_idx = classes.index("HOME_TEAM")
draw_idx = classes.index("DRAW")
away_idx = classes.index("AWAY_TEAM")

# ── lookup tables ─────────────────────────────────────────────────────────────

teams_df = pd.read_sql("SELECT id, api_id, name FROM whowillwin.teams", engine)
team_names     = dict(zip(teams_df["api_id"].astype(str), teams_df["name"]))
api_id_to_uuid = dict(zip(teams_df["api_id"].astype(str), teams_df["id"].astype(str)))

# current rolling stats snapshot (last row per team after processing all played matches)
current_stats: dict = {
    str(t): {
        "home_avg_goals":    safe_mean(team_stats[t]["scored"]),
        "away_avg_goals":    safe_mean(team_stats[t]["scored"]),
        "home_avg_conceded": safe_mean(team_stats[t]["conceded"]),
        "away_avg_conceded": safe_mean(team_stats[t]["conceded"]),
        "home_win_rate":     safe_mean(team_stats[t]["wins"]),
        "away_win_rate":     safe_mean(team_stats[t]["wins"]),
    }
    for t in team_stats
}

# ── helpers ───────────────────────────────────────────────────────────────────

def _predict_proba(home_id: str, away_id: str, matchday: int) -> tuple[float, float, float]:
    home_s = current_stats.get(home_id)
    away_s = current_stats.get(away_id)
    if not home_s or not away_s:
        raise HTTPException(status_code=404, detail="No match data for team")
    features = [[
        matchday,
        home_s["home_avg_goals"],
        away_s["away_avg_goals"],
        home_s["home_avg_conceded"],
        away_s["away_avg_conceded"],
        home_s["home_win_rate"],
        away_s["away_win_rate"],
    ]]
    proba = model.predict_proba(features)[0]
    return round(float(proba[home_idx]) * 100, 1), \
           round(float(proba[draw_idx]) * 100, 1), \
           round(float(proba[away_idx]) * 100, 1)

# ── endpoints ─────────────────────────────────────────────────────────────────

@app.get("/predict")
def predict(homeTeamId: int, awayTeamId: int, matchday: int = 1):
    home_uuid = api_id_to_uuid.get(str(homeTeamId))
    away_uuid = api_id_to_uuid.get(str(awayTeamId))
    if not home_uuid or not away_uuid:
        raise HTTPException(status_code=404, detail="Team not found")

    hw, d, aw = _predict_proba(home_uuid, away_uuid, matchday)
    return {
        "homeTeam":      team_names.get(str(homeTeamId), str(homeTeamId)),
        "awayTeam":      team_names.get(str(awayTeamId), str(awayTeamId)),
        "homeWinChance": hw,
        "drawChance":    d,
        "awayWinChance": aw,
    }


@app.get("/future-predictions")
def future_predictions():
    """Return ML predictions for all unplayed matches."""
    if df_future.empty:
        return []

    probs = model.predict_proba(df_future[FEATURES])
    results = []
    for i, (_, row) in enumerate(df_future.iterrows()):
        results.append({
            "homeTeamId":    int(row["home_api_id"]),
            "awayTeamId":    int(row["away_api_id"]),
            "matchday":      int(row["matchday"]),
            "homeWinChance": round(float(probs[i][home_idx]) * 100, 1),
            "drawChance":    round(float(probs[i][draw_idx]) * 100, 1),
            "awayWinChance": round(float(probs[i][away_idx]) * 100, 1),
        })
    return results
