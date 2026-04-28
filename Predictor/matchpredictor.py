import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres")
df = pd.read_sql("SELECT * FROM whowillwin.matches", engine)

df = df[[
    "season",
    "matchday",
    "utc_date",
    "home_team_id",
    "away_team_id",
    "home_goals",
    "away_goals",
    "winner"
]]

df = df.sort_values("utc_date").reset_index(drop=True)

df_finished = df[df["winner"].notna()].copy()
df_future   = df[df["winner"].isna()].copy()

print("Finished:", len(df_finished))
print("Future:  ", len(df_future))

# ── Historical stats loop ──────────────────────────────────────────────────
team_stats = {}

home_avg_goals = []
away_avg_goals = []
home_win_rate  = []
away_win_rate  = []

def safe_mean(lst):
    return float(sum(lst) / len(lst)) if lst else 0.0

for _, row in df.iterrows():
    home = row["home_team_id"]
    away = row["away_team_id"]

    if home not in team_stats:
        team_stats[home] = {"scored": [], "conceded": [], "wins": []}
    if away not in team_stats:
        team_stats[away] = {"scored": [], "conceded": [], "wins": []}

    # Read BEFORE updating
    home_avg_goals.append(safe_mean(team_stats[home]["scored"]))
    away_avg_goals.append(safe_mean(team_stats[away]["scored"]))
    home_win_rate.append(safe_mean(team_stats[home]["wins"]))
    away_win_rate.append(safe_mean(team_stats[away]["wins"]))

    # Update ONLY if match is finished
    hg = row["home_goals"]
    ag = row["away_goals"]
    if not pd.isna(hg) and not pd.isna(ag):
        team_stats[home]["scored"].append(hg)
        team_stats[away]["scored"].append(ag)

        if hg > ag:
            team_stats[home]["wins"].append(1)
            team_stats[away]["wins"].append(0)
        elif hg < ag:
            team_stats[home]["wins"].append(0)
            team_stats[away]["wins"].append(1)
        else:
            team_stats[home]["wins"].append(0)
            team_stats[away]["wins"].append(0)

df["home_avg_goals"] = home_avg_goals
df["away_avg_goals"] = away_avg_goals
df["home_win_rate"]  = home_win_rate
df["away_win_rate"]  = away_win_rate

print(df[["home_avg_goals", "away_avg_goals", "home_win_rate", "away_win_rate"]].iloc[50:55])