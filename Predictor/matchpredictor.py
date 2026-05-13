import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import RFE
from scipy.stats import zscore

engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres")
df = pd.read_sql("SELECT * FROM whowillwin.matches", engine)
teams = pd.read_sql("SELECT id, name FROM whowillwin.teams", engine)
standings = pd.read_sql("SELECT * FROM whowillwin.standings WHERE type = 'TOTAL'", engine)
h2h = pd.read_sql("SELECT * FROM whowillwin.head_to_head", engine)

team_map = dict(zip(teams["id"], teams["name"]))

df = df[[
    "season", "matchday", "utc_date",
    "home_team_id", "away_team_id",
    "home_goals", "away_goals", "winner"
]]

df = df.sort_values("utc_date").reset_index(drop=True)

df["home_goals"] = df["home_goals"].clip(upper=5)
df["away_goals"] = df["away_goals"].clip(upper=5)

# ── Manual rolling stats ───────────────────────────────────────────────────
team_stats = {}

home_avg_goals         = []
away_avg_goals         = []
home_win_rate_weighted = []
away_win_rate_weighted = []

def safe_mean(lst):
    return float(sum(lst) / len(lst)) if lst else 0.0

for _, row in df.iterrows():
    home = row["home_team_id"]
    away = row["away_team_id"]

    if home not in team_stats:
        team_stats[home] = {"scored": [], "wins": []}
    if away not in team_stats:
        team_stats[away] = {"scored": [], "wins": []}

    hmp = len(team_stats[home]["wins"])
    amp = len(team_stats[away]["wins"])
    hwr = safe_mean(team_stats[home]["wins"])
    awr = safe_mean(team_stats[away]["wins"])

    home_avg_goals.append(safe_mean(team_stats[home]["scored"]))
    away_avg_goals.append(safe_mean(team_stats[away]["scored"]))
    home_win_rate_weighted.append(hwr * min(hmp / 38, 1.0))
    away_win_rate_weighted.append(awr * min(amp / 38, 1.0))

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

df["home_avg_goals"]         = home_avg_goals
df["away_avg_goals"]         = away_avg_goals
df["home_win_rate_weighted"] = home_win_rate_weighted
df["away_win_rate_weighted"] = away_win_rate_weighted

# ── Join standings (previous matchday) ────────────────────────────────────
std = standings[["team_id", "season", "matchday", "position", "points", "goal_diff", "won", "drawn", "lost"]].copy()
std["matchday"] = std["matchday"] + 1

df = df.merge(
    std.rename(columns={
        "team_id":   "home_team_id",
        "position":  "home_position",
        "points":    "home_points",
        "goal_diff": "home_goal_diff",
        "won":       "home_won",
        "drawn":     "home_drawn",
        "lost":      "home_lost",
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
        "won":       "away_won",
        "drawn":     "away_drawn",
        "lost":      "away_lost",
    }),
    on=["away_team_id", "season", "matchday"],
    how="left"
)

standings_cols = [
    "home_position", "home_points", "home_goal_diff", "home_won", "home_drawn", "home_lost",
    "away_position", "away_points", "away_goal_diff", "away_won", "away_drawn", "away_lost",
]
df[standings_cols] = df[standings_cols].fillna(0)

# ── Join head to head ──────────────────────────────────────────────────────
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

h2h_total     = []
h2h_home_wins = []
h2h_draws     = []
h2h_away_wins = []
h2h_avg_goals = []

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

# ── 13 selected features (after RFE + correlation + importances analysis) ──
FEATURES = [
    "home_avg_goals", "away_avg_goals",
    "home_win_rate_weighted", "away_win_rate_weighted",
    "home_points", "away_points",
    "home_position", "away_position",
    "home_goal_diff", "away_goal_diff",
    "h2h_home_wins", "h2h_away_wins", "h2h_draws",
]

df_train  = df[df["winner"].notna()].copy()
df_future = df[df["winner"].isna()].copy()

X = df_train[FEATURES]
y = df_train["winner"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

model = SVC(kernel='rbf', class_weight='balanced', random_state=42, probability=True)
model.fit(X_train_scaled, y_train)
pred = model.predict(X_test_scaled)

print("\n── SVM 13 features ──")
print(classification_report(y_test, pred))

# ── RFE chart ─────────────────────────────────────────────────────────────
rfe = RFE(RandomForestClassifier(n_estimators=100, random_state=42), n_features_to_select=10)
rfe.fit(X, y)

rfe_ranking = sorted(zip(FEATURES, rfe.ranking_), key=lambda x: x[1])

plt.figure(figsize=(10, 7))
colors_rfe = ["steelblue" if r == 1 else "lightcoral" for _, r in rfe_ranking]
plt.barh([f[0] for f in rfe_ranking], [1/r[1] for r in rfe_ranking], color=colors_rfe, edgecolor="black", linewidth=0.8)
plt.xlabel("RFE Score (higher = more important)")
plt.title("RFE — Feature Selection")
plt.tight_layout()
plt.show()

# ── Feature importances (RFC for reference) ───────────────────────────────
rfc_ref = RandomForestClassifier(n_estimators=200, random_state=42, class_weight='balanced')
rfc_ref.fit(X, y)

importances = rfc_ref.feature_importances_
indices = sorted(range(len(importances)), key=lambda i: importances[i])

plt.figure(figsize=(10, 8))
plt.barh(
    [FEATURES[i] for i in indices],
    [importances[i] for i in indices],
    edgecolor='black', linewidth=0.8
)
plt.xlabel("Importance")
plt.title("Feature Importances — Random Forest")
plt.tight_layout()
plt.show()

# ── Predict future matches ─────────────────────────────────────────────────
X_future_scaled = scaler.transform(df_future[FEATURES])
probs = model.predict_proba(X_future_scaled)

classes  = list(model.classes_)
home_idx = classes.index("HOME_TEAM")
draw_idx = classes.index("DRAW")
away_idx = classes.index("AWAY_TEAM")

results = df_future[["utc_date", "home_team_id", "away_team_id"]].copy()
results["home_win"] = (probs[:, home_idx] * 100).round(1)
results["draw"]     = (probs[:, draw_idx] * 100).round(1)
results["away_win"] = (probs[:, away_idx] * 100).round(1)

results["home_team"] = results["home_team_id"].map(team_map)
results["away_team"] = results["away_team_id"].map(team_map)

results = results[["utc_date", "home_team", "away_team", "home_win", "draw", "away_win"]]

# ── Export CSVs ───────────────────────────────────────────────────────────
df_train[FEATURES + ["winner"]].to_csv("features_sample.csv", index=False)
results.to_csv("predictions.csv", index=False)
