import pandas as pd
from sqlalchemy import create_engine
import numpy as np

engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres")
df = pd.read_sql("SELECT * FROM whowillwin.matches", engine)

df.to_csv("matches.csv", index=False)

df = df[["season", "matchday", "utc_date", "home_team_id", "away_team_id", "home_goals", "away_goals", "winner"]]
df = df.dropna(subset=["home_goals", "away_goals", "winner"])


df["result"] = df["winner"].map({"HOME_TEAM": 0, "DRAW": 1, "AWAY_TEAM": 2})


df.groupby("home_team_id")["home_goals"].mean()
home_stats = df.groupby("home_team_id")["home_goals"].mean()
away_stats = df.groupby("away_team_id")["away_goals"].mean()

home_wins = df.groupby("home_team_id")["result"].apply(lambda x: (x == 0).mean())
away_wins = df.groupby("away_team_id")["result"].apply(lambda x: (x == 2).mean())

print(home_wins)
print(away_wins)

# print(df)