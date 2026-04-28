import pandas as pd
from sqlalchemy import create_engine
from sklearn.linear_model import LogisticRegression
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

df = pd.read_sql("SELECT * FROM whowillwin.matches", engine)
df = df[["home_team_id", "away_team_id", "home_goals", "away_goals", "winner"]]
df = df.dropna(subset=["home_goals", "away_goals", "winner"])
df["result"] = df["winner"].map({"HOME_TEAM": 0, "DRAW": 1, "AWAY_TEAM": 2})

home_goals = df.groupby("home_team_id")["home_goals"].mean()
away_goals = df.groupby("away_team_id")["away_goals"].mean()
home_wins = df.groupby("home_team_id")["result"].apply(lambda x: (x == 0).mean())
away_wins = df.groupby("away_team_id")["result"].apply(lambda x: (x == 2).mean())

df["home_goals_per_game"] = df["home_team_id"].map(home_goals)
df["away_goals_per_game"] = df["away_team_id"].map(away_goals)
df["home_win_rate"] = df["home_team_id"].map(home_wins)
df["away_win_rate"] = df["away_team_id"].map(away_wins)

X = df[["home_goals_per_game", "away_goals_per_game", "home_win_rate", "away_win_rate"]]
y = df["result"]

clf = LogisticRegression(random_state=0).fit(X, y)

team_features = {}
for team_id in df["home_team_id"].unique():
    team_features[str(team_id)] = {
        "home_goals_per_game": home_goals.get(team_id, X["home_goals_per_game"].mean()),
        "home_win_rate": home_wins.get(team_id, X["home_win_rate"].mean()),
        "away_goals_per_game": away_goals.get(team_id, X["away_goals_per_game"].mean()),
        "away_win_rate": away_wins.get(team_id, X["away_win_rate"].mean()),
    }

teams_df = pd.read_sql("SELECT api_id, name FROM whowillwin.teams", engine)
team_names = dict(zip(teams_df["api_id"].astype(str), teams_df["name"]))

uuid_by_api_id = pd.read_sql("SELECT id, api_id FROM whowillwin.teams", engine)
uuid_by_api_id["id"] = uuid_by_api_id["id"].astype(str)
uuid_by_api_id["api_id"] = uuid_by_api_id["api_id"].astype(str)
api_id_to_uuid = dict(zip(uuid_by_api_id["api_id"], uuid_by_api_id["id"]))


@app.get("/predict")
def predict(homeTeamId: int, awayTeamId: int):
    home_uuid = api_id_to_uuid.get(str(homeTeamId))
    away_uuid = api_id_to_uuid.get(str(awayTeamId))

    if not home_uuid or not away_uuid:
        raise HTTPException(status_code=404, detail="Team not found")

    home = team_features.get(home_uuid)
    away = team_features.get(away_uuid)

    if not home or not away:
        raise HTTPException(status_code=404, detail="No match data for team")

    features = [[
        home["home_goals_per_game"],
        away["away_goals_per_game"],
        home["home_win_rate"],
        away["away_win_rate"],
    ]]

    proba = clf.predict_proba(features)[0]

    return {
        "homeTeam": team_names.get(str(homeTeamId), str(homeTeamId)),
        "awayTeam": team_names.get(str(awayTeamId), str(awayTeamId)),
        "homeWinChance": round(float(proba[0]), 4),
        "drawChance": round(float(proba[1]), 4),
        "awayWinChance": round(float(proba[2]), 4),
    }