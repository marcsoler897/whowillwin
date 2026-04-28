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

team_stats = {}

home_avg_goals    = []
away_avg_goals    = []
home_avg_conceded = []
away_avg_conceded = []
home_win_rate     = []
away_win_rate     = []

def safe_mean(lst):
    return float(sum(lst) / len(lst)) if lst else 0.0

for _, row in df.iterrows():
    home = row["home_team_id"]
    away = row["away_team_id"]

    if home not in team_stats:
        team_stats[home] = {"scored": [], "conceded": [], "wins": []}
    if away not in team_stats:
        team_stats[away] = {"scored": [], "conceded": [], "wins": []}

    home_avg_goals.append(safe_mean(team_stats[home]["scored"]))
    away_avg_goals.append(safe_mean(team_stats[away]["scored"]))
    home_avg_conceded.append(safe_mean(team_stats[home]["conceded"]))
    away_avg_conceded.append(safe_mean(team_stats[away]["conceded"]))
    home_win_rate.append(safe_mean(team_stats[home]["wins"]))
    away_win_rate.append(safe_mean(team_stats[away]["wins"]))

    hg = row["home_goals"]
    ag = row["away_goals"]
    if not pd.isna(hg) and not pd.isna(ag):
        team_stats[home]["scored"].append(hg)
        team_stats[home]["conceded"].append(ag)
        team_stats[away]["scored"].append(ag)
        team_stats[away]["conceded"].append(hg)

        if hg > ag:
            team_stats[home]["wins"].append(1)
            team_stats[away]["wins"].append(0)
        elif hg < ag:
            team_stats[home]["wins"].append(0)
            team_stats[away]["wins"].append(1)
        else:
            team_stats[home]["wins"].append(0)
            team_stats[away]["wins"].append(0)

df["home_avg_goals"]    = home_avg_goals
df["away_avg_goals"]    = away_avg_goals
df["home_avg_conceded"] = home_avg_conceded
df["away_avg_conceded"] = away_avg_conceded
df["home_win_rate"]     = home_win_rate
df["away_win_rate"]     = away_win_rate

from sklearn.ensemble import RandomForestClassifier

FEATURES = [
    "matchday",
    "home_avg_goals",
    "away_avg_goals",
    "home_avg_conceded",
    "away_avg_conceded",
    "home_win_rate",
    "away_win_rate",
]

df_train  = df[df["winner"].notna()].copy()
df_future = df[df["winner"].isna()].copy()

X = df_train[FEATURES]
y = df_train["winner"]

model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X, y)

X_future = df_future[FEATURES]
probs = model.predict_proba(X_future)

results = df_future[["utc_date", "home_team_id", "away_team_id"]].copy()
results["home_win"] = (probs[:, list(model.classes_).index("HOME_TEAM")] * 100).round(1)
results["draw"]     = (probs[:, list(model.classes_).index("DRAW")] * 100).round(1)
results["away_win"] = (probs[:, list(model.classes_).index("AWAY_TEAM")] * 100).round(1)

print(results.to_string(index=False))