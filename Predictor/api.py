import pandas as pd
from sqlalchemy import create_engine
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
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

# ── load data ─────────────────────────────────────────────────────────────────

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

standings = pd.read_sql(
    "SELECT * FROM whowillwin.standings WHERE type = 'TOTAL'", engine
)
h2h = pd.read_sql("SELECT * FROM whowillwin.head_to_head", engine)
scorers = pd.read_sql("SELECT team_id, season, goals, assists, penalties FROM whowillwin.scorers", engine)

df = df[[
    "season", "matchday", "utc_date",
    "home_team_id", "away_team_id",
    "home_api_id", "away_api_id",
    "home_goals", "away_goals", "winner",
]]
df = df.sort_values("utc_date").reset_index(drop=True)

df["home_goals"] = df["home_goals"].clip(upper=5)
df["away_goals"] = df["away_goals"].clip(upper=5)

# ── build rolling features ────────────────────────────────────────────────────

team_stats: dict = {}

home_avg_goals, away_avg_goals = [], []
home_win_rate_weighted, away_win_rate_weighted = [], []

def safe_mean(lst):
    return float(sum(lst) / len(lst)) if lst else 0.0

for _, row in df.iterrows():
    home = row["home_team_id"]
    away = row["away_team_id"]

    for t in (home, away):
        if t not in team_stats:
            team_stats[t] = {"scored": [], "wins": []}

    hmp = len(team_stats[home]["wins"])
    amp = len(team_stats[away]["wins"])
    hwr = safe_mean(team_stats[home]["wins"])
    awr = safe_mean(team_stats[away]["wins"])

    home_avg_goals.append(safe_mean(team_stats[home]["scored"]))
    away_avg_goals.append(safe_mean(team_stats[away]["scored"]))
    home_win_rate_weighted.append(hwr * min(hmp / 38, 1.0))
    away_win_rate_weighted.append(awr * min(amp / 38, 1.0))

    hg, ag = row["home_goals"], row["away_goals"]
    if not pd.isna(hg) and not pd.isna(ag):
        team_stats[home]["scored"].append(hg)
        team_stats[away]["scored"].append(ag)
        if hg > ag:
            team_stats[home]["wins"].append(1); team_stats[away]["wins"].append(0)
        elif hg < ag:
            team_stats[home]["wins"].append(0); team_stats[away]["wins"].append(1)
        else:
            team_stats[home]["wins"].append(0); team_stats[away]["wins"].append(0)

df["home_avg_goals"]         = home_avg_goals
df["away_avg_goals"]         = away_avg_goals
df["home_win_rate_weighted"] = home_win_rate_weighted
df["away_win_rate_weighted"] = away_win_rate_weighted

# ── join standings (previous matchday) ───────────────────────────────────────

std = standings[["team_id", "season", "matchday", "position", "points", "goal_diff"]].copy()
std["matchday"] = std["matchday"] + 1

df = df.merge(
    std.rename(columns={
        "team_id":   "home_team_id",
        "position":  "home_position",
        "points":    "home_points",
        "goal_diff": "home_goal_diff",
    }),
    on=["home_team_id", "season", "matchday"],
    how="left"
)

df = df.merge(
    std.rename(columns={
        "team_id":   "away_team_id",
        "position":  "away_position",
        "points":    "away_points",
        "goal_diff": "away_goal_diff",
    }),
    on=["away_team_id", "season", "matchday"],
    how="left"
)

standings_cols = [
    "home_position", "home_points", "home_goal_diff",
    "away_position", "away_points", "away_goal_diff",
]
df[standings_cols] = df[standings_cols].fillna(0)

# ── join head to head ─────────────────────────────────────────────────────────

def get_h2h_stats(home_id, away_id, h2h_df):
    if home_id < away_id:
        t1, t2 = home_id, away_id
        home_is_t1 = True
    else:
        t1, t2 = away_id, home_id
        home_is_t1 = False

    row = h2h_df[(h2h_df["team1_id"] == t1) & (h2h_df["team2_id"] == t2)]
    if row.empty:
        return 0, 0, 0, 0, 0

    r = row.iloc[0]
    total = r["total_matches"]
    draws = r["draws"]
    avg_goals = r["total_goals"] / total if total > 0 else 0

    if home_is_t1:
        home_wins = r["team1_wins"]
        away_wins = r["team2_wins"]
    else:
        home_wins = r["team2_wins"]
        away_wins = r["team1_wins"]

    return total, home_wins, draws, away_wins, avg_goals

h2h_total, h2h_home_wins, h2h_draws, h2h_away_wins, h2h_avg_goals = [], [], [], [], []

for _, row in df.iterrows():
    total, hw, d, aw, ag = get_h2h_stats(row["home_team_id"], row["away_team_id"], h2h)
    h2h_total.append(total)
    h2h_home_wins.append(hw)
    h2h_draws.append(d)
    h2h_away_wins.append(aw)
    h2h_avg_goals.append(ag)

df["h2h_total"]     = h2h_total
df["h2h_home_wins"] = h2h_home_wins
df["h2h_draws"]     = h2h_draws
df["h2h_away_wins"] = h2h_away_wins
df["h2h_avg_goals"] = h2h_avg_goals

# ── join scorers ──────────────────────────────────────────────────────────────

df = df.merge(
    scorers.rename(columns={"team_id": "home_team_id", "goals": "home_scorer_goals",
                             "assists": "home_scorer_assists", "penalties": "home_scorer_penalties"}),
    on=["home_team_id", "season"], how="left"
)
df = df.merge(
    scorers.rename(columns={"team_id": "away_team_id", "goals": "away_scorer_goals",
                             "assists": "away_scorer_assists", "penalties": "away_scorer_penalties"}),
    on=["away_team_id", "season"], how="left"
)
scorer_cols = ["home_scorer_goals", "away_scorer_goals", "home_scorer_assists", "away_scorer_assists",
               "home_scorer_penalties", "away_scorer_penalties"]
df[scorer_cols] = df[scorer_cols].fillna(0)

# ── train model ───────────────────────────────────────────────────────────────

FEATURES = [
    "home_avg_goals", "away_avg_goals",
    "home_win_rate_weighted", "away_win_rate_weighted",
    "home_points", "away_points",
    "home_goal_diff", "away_goal_diff",
    "h2h_home_wins", "h2h_away_wins", "h2h_draws",
    "home_scorer_goals", "away_scorer_goals",
]

df_train  = df[df["winner"].notna()].copy()
df_future = df[df["winner"].isna()].copy()

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(df_train[FEATURES])

model = SVC(kernel='rbf', C=100, gamma=0.001, class_weight='balanced', random_state=42, probability=True)
model.fit(X_train_scaled, df_train["winner"])

classes  = list(model.classes_)
home_idx = classes.index("HOME_TEAM")
draw_idx = classes.index("DRAW")
away_idx = classes.index("AWAY_TEAM")

# ── lookup tables ─────────────────────────────────────────────────────────────

teams_df = pd.read_sql("SELECT id, api_id, name FROM whowillwin.teams", engine)
team_names     = dict(zip(teams_df["api_id"].astype(str), teams_df["name"]))
api_id_to_uuid = dict(zip(teams_df["api_id"].astype(str), teams_df["id"].astype(str)))

# latest standings snapshot per team (most recent matchday available)
latest_standings = (
    standings.sort_values("matchday")
    .groupby("team_id")
    .last()
    .reset_index()
)[["team_id", "points", "goal_diff"]]
standings_map: dict = {
    str(row["team_id"]): {
        "points":    float(row["points"]),
        "goal_diff": float(row["goal_diff"]),
    }
    for _, row in latest_standings.iterrows()
}

# scorers snapshot: most recent season per team
scorers_map: dict = {}
for _, row in scorers.sort_values("season").iterrows():
    scorers_map[str(row["team_id"])] = {
        "home_scorer_goals": float(row["goals"]),
        "away_scorer_goals": float(row["goals"]),
    }

# current rolling stats snapshot after all played matches
current_stats: dict = {
    str(t): {
        "home_avg_goals":         safe_mean(team_stats[t]["scored"]),
        "away_avg_goals":         safe_mean(team_stats[t]["scored"]),
        "home_win_rate_weighted": safe_mean(team_stats[t]["wins"]) * min(len(team_stats[t]["wins"]) / 38, 1.0),
        "away_win_rate_weighted": safe_mean(team_stats[t]["wins"]) * min(len(team_stats[t]["wins"]) / 38, 1.0),
    }
    for t in team_stats
}

# ── helpers ───────────────────────────────────────────────────────────────────

def _predict_proba(home_id: str, away_id: str) -> tuple[float, float, float]:
    home_s = current_stats.get(home_id)
    away_s = current_stats.get(away_id)
    if not home_s or not away_s:
        raise HTTPException(status_code=404, detail="No match data for team")

    default_st = {"points": 0.0, "goal_diff": 0.0}
    home_st = standings_map.get(home_id, default_st)
    away_st = standings_map.get(away_id, default_st)

    default_sc = {"home_scorer_goals": 0.0, "away_scorer_goals": 0.0}
    home_sc = scorers_map.get(home_id, default_sc)
    away_sc = scorers_map.get(away_id, default_sc)

    _, h2h_hw, h2h_d, h2h_aw, _ = get_h2h_stats(home_id, away_id, h2h)

    features = [[
        home_s["home_avg_goals"],
        away_s["away_avg_goals"],
        home_s["home_win_rate_weighted"],
        away_s["away_win_rate_weighted"],
        home_st["points"],
        away_st["points"],
        home_st["goal_diff"],
        away_st["goal_diff"],
        h2h_hw,
        h2h_aw,
        h2h_d,
        home_sc["home_scorer_goals"],
        away_sc["away_scorer_goals"],
    ]]
    features_scaled = scaler.transform(features)
    proba = model.predict_proba(features_scaled)[0]
    return (
        round(float(proba[home_idx]) * 100, 1),
        round(float(proba[draw_idx]) * 100, 1),
        round(float(proba[away_idx]) * 100, 1),
    )

# ── endpoints ─────────────────────────────────────────────────────────────────

@app.get("/predict")
def predict(homeTeamId: int, awayTeamId: int):
    home_uuid = api_id_to_uuid.get(str(homeTeamId))
    away_uuid = api_id_to_uuid.get(str(awayTeamId))
    if not home_uuid or not away_uuid:
        raise HTTPException(status_code=404, detail="Team not found")

    hw, d, aw = _predict_proba(home_uuid, away_uuid)
    return {
        "homeTeam":      team_names.get(str(homeTeamId), str(homeTeamId)),
        "awayTeam":      team_names.get(str(awayTeamId), str(awayTeamId)),
        "homeWinChance": hw,
        "drawChance":    d,
        "awayWinChance": aw,
    }


@app.get("/future-predictions")
def future_predictions():
    """Return SVM predictions for all unplayed matches."""
    if df_future.empty:
        return []

    X_future_scaled = scaler.transform(df_future[FEATURES])
    probs = model.predict_proba(X_future_scaled)
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
