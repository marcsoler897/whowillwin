import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres")
df = pd.read_sql("SELECT * FROM whowillwin.matches", engine)
teams = pd.read_sql("SELECT id, name FROM whowillwin.teams", engine)

team_map = dict(zip(teams["id"], teams["name"]))

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

# ── EDA ────────────────────────────────────────────────────────────────────
print("── Shape ──")
print(df.shape)

print("\n── Missing values ──")
print(df.isnull().sum())

print("\n── Winner distribution ──")
print(df["winner"].value_counts())

print("\n── Goals stats ──")
print(df[["home_goals", "away_goals"]].describe())

print("\n── Outlier check (home_goals) ──")
Q1 = df["home_goals"].quantile(0.25)
Q3 = df["home_goals"].quantile(0.75)
IQR = Q3 - Q1
outliers = df[(df["home_goals"] < Q1 - 1.5 * IQR) | (df["home_goals"] > Q3 + 1.5 * IQR)]
print(f"Outlier matches: {len(outliers)}")

plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
sns.histplot(df["home_goals"].dropna(), bins=10)
plt.title("Home Goals Distribution")
plt.subplot(1, 2, 2)
sns.histplot(df["away_goals"].dropna(), bins=10)
plt.title("Away Goals Distribution")
plt.tight_layout()

# ── Processing ─────────────────────────────────────────────────────────────
df = df.sort_values("utc_date").reset_index(drop=True)

# Cap outliers at 5 goals
df["home_goals"] = df["home_goals"].clip(upper=5)
df["away_goals"] = df["away_goals"].clip(upper=5)

team_stats = {}

home_avg_goals = []
away_avg_goals = []
home_win_rate  = []
away_win_rate  = []
home_form5     = []
away_form5     = []

def safe_mean(lst):
    return float(sum(lst) / len(lst)) if lst else 0.0

for _, row in df.iterrows():
    home = row["home_team_id"]
    away = row["away_team_id"]

    if home not in team_stats:
        team_stats[home] = {"scored": [], "wins": []}
    if away not in team_stats:
        team_stats[away] = {"scored": [], "wins": []}

    home_avg_goals.append(safe_mean(team_stats[home]["scored"]))
    away_avg_goals.append(safe_mean(team_stats[away]["scored"]))
    home_win_rate.append(safe_mean(team_stats[home]["wins"]))
    away_win_rate.append(safe_mean(team_stats[away]["wins"]))
    home_form5.append(safe_mean(team_stats[home]["wins"][-5:]))
    away_form5.append(safe_mean(team_stats[away]["wins"][-5:]))

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
df["home_form5"]     = home_form5
df["away_form5"]     = away_form5

# ── Box plots ──────────────────────────────────────────────────────────────
df_plot = df[df["winner"].notna()].copy()

plt.figure(figsize=(15, 10))

plt.subplot(2, 3, 1)
sns.boxplot(x="winner", y="home_avg_goals", data=df_plot)
plt.title("Home Avg Goals")

plt.subplot(2, 3, 2)
sns.boxplot(x="winner", y="away_avg_goals", data=df_plot)
plt.title("Away Avg Goals")

plt.subplot(2, 3, 3)
sns.boxplot(x="winner", y="home_win_rate", data=df_plot)
plt.title("Home Win Rate")

plt.subplot(2, 3, 4)
sns.boxplot(x="winner", y="away_win_rate", data=df_plot)
plt.title("Away Win Rate")

plt.subplot(2, 3, 5)
sns.boxplot(x="winner", y="home_form5", data=df_plot)
plt.title("Home Form (Last 5)")

plt.subplot(2, 3, 6)
sns.boxplot(x="winner", y="away_form5", data=df_plot)
plt.title("Away Form (Last 5)")

plt.tight_layout()
plt.show()

# ── Model ──────────────────────────────────────────────────────────────────
FEATURES = [
    "matchday",
    "home_avg_goals",
    "away_avg_goals",
    "home_win_rate",
    "away_win_rate",
    "home_form5",
    "away_form5",
]

df_train  = df[df["winner"].notna()].copy()
df_future = df[df["winner"].isna()].copy()

X = df_train[FEATURES]
y = df_train["winner"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model_test = RandomForestClassifier(n_estimators=200, random_state=42)
model_test.fit(X_train, y_train)
print("── Model accuracy on test set ──")
print(classification_report(y_test, model_test.predict(X_test)))

model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X, y)

X_future = df_future[FEATURES]
probs = model.predict_proba(X_future)

results = df_future[["utc_date", "home_team_id", "away_team_id"]].copy()
results["home_win"] = (probs[:, list(model.classes_).index("HOME_TEAM")] * 100).round(1)
results["draw"]     = (probs[:, list(model.classes_).index("DRAW")] * 100).round(1)
results["away_win"] = (probs[:, list(model.classes_).index("AWAY_TEAM")] * 100).round(1)

results["home_team"] = results["home_team_id"].map(team_map)
results["away_team"] = results["away_team_id"].map(team_map)

results = results[["utc_date", "home_team", "away_team", "home_win", "draw", "away_win"]]

print(results.to_string(index=False))