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

df["home_goals_per_game"] = df["home_team_id"].map(home_stats)
df["away_goals_per_game"] = df["away_team_id"].map(away_stats)
df["home_win_rate"] = df["home_team_id"].map(home_wins)
df["away_win_rate"] = df["away_team_id"].map(away_wins)

X = df[["home_goals_per_game", "away_goals_per_game", "home_win_rate", "away_win_rate"]]
y = df["result"]

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

from sklearn.linear_model import LogisticRegression
clf = LogisticRegression(random_state=0).fit(X_train, y_train)
print(clf.predict(X_test[:5]))
print(clf.predict_proba(X_test[:5]))
print(clf.score(X_test, y_test))