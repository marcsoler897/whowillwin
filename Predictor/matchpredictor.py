import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from scipy.stats import zscore

engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres")
df = pd.read_sql("SELECT * FROM whowillwin.matches", engine)
teams = pd.read_sql("SELECT id, name FROM whowillwin.teams", engine)
standings = pd.read_sql("SELECT * FROM whowillwin.standings WHERE type = 'TOTAL'", engine)
h2h = pd.read_sql("SELECT * FROM whowillwin.head_to_head", engine)
scorers = pd.read_sql("SELECT team_id, season, goals, assists, penalties FROM whowillwin.scorers", engine)

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
std = standings[["team_id", "season", "matchday", "position", "points", "goal_diff", "goals_against", "won", "drawn", "lost"]].copy()
std["matchday"] = std["matchday"] + 1

df = df.merge(
    std.rename(columns={
        "team_id":      "home_team_id",
        "position":     "home_position",
        "points":       "home_points",
        "goal_diff":    "home_goal_diff",
        "goals_against":"home_goals_against",
        "won":          "home_won",
        "drawn":        "home_drawn",
        "lost":         "home_lost",
    }),
    on=["home_team_id", "season", "matchday"],
    how="left"
)

df = df.merge(
    std.rename(columns={
        "team_id":      "away_team_id",
        "position":     "away_position",
        "points":       "away_points",
        "goal_diff":    "away_goal_diff",
        "goals_against":"away_goals_against",
        "won":          "away_won",
        "drawn":        "away_drawn",
        "lost":         "away_lost",
    }),
    on=["away_team_id", "season", "matchday"],
    how="left"
)

standings_cols = [
    "home_position", "home_points", "home_goal_diff", "home_goals_against", "home_won", "home_drawn", "home_lost",
    "away_position", "away_points", "away_goal_diff", "away_goals_against", "away_won", "away_drawn", "away_lost",
]
df[standings_cols] = df[standings_cols].fillna(0)

home_played = df["home_won"] + df["home_drawn"] + df["home_lost"]
away_played = df["away_won"] + df["away_drawn"] + df["away_lost"]
df["home_draw_rate"] = df["home_drawn"] / home_played.replace(0, 1)
df["away_draw_rate"] = df["away_drawn"] / away_played.replace(0, 1)

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
df["h2h_draw_rate"] = [d / t if t > 0 else 0.0 for d, t in zip(h2h_draws, h2h_total)]

# ── Join scorers (season-level team goal totals) ───────────────────────────
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

# ── 15 features (13 + 2 scorer goal columns) ──────────────────────────────
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

X = df_train[FEATURES]
y = df_train["winner"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

model = SVC(kernel='rbf', C=100, gamma=0.001, class_weight='balanced', random_state=42, probability=True)
model.fit(X_train_scaled, y_train)
pred = model.predict(X_test_scaled)

print("\n── SVM 15 features ──")
print(classification_report(y_test, pred))

# ── Cross-validation (5 folds) ────────────────────────────────────────────
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline

cv_model = make_pipeline(
    StandardScaler(),
    SVC(kernel='rbf', C=100, gamma=0.001, class_weight='balanced', random_state=42)
)
scores = cross_val_score(cv_model, X, y, cv=5, scoring='accuracy')
print("\n── 5-Fold Cross-Validation ──")
for i, s in enumerate(scores, 1):
    print(f"  Fold {i}: {s*100:.1f}%")
print(f"  Mean:   {scores.mean()*100:.1f}% ± {scores.std()*100:.1f}%")

# ── Grid search (C + gamma) ───────────────────────────────────────────────
from sklearn.model_selection import GridSearchCV

param_grid = {
    "svc__C":     [0.1, 1, 10, 100],
    "svc__gamma": ["scale", "auto", 0.001, 0.01, 0.1],
}
grid = GridSearchCV(
    make_pipeline(StandardScaler(), SVC(kernel='rbf', class_weight='balanced', random_state=42, probability=True)),
    param_grid, cv=5, scoring='accuracy', n_jobs=-1, verbose=0
)
grid.fit(X, y)
print("\n── Grid Search Best Params ──")
print(f"  C:     {grid.best_params_['svc__C']}")
print(f"  gamma: {grid.best_params_['svc__gamma']}")
print(f"  CV accuracy: {grid.best_score_*100:.1f}%")
print(f"\n  Difference: {(grid.best_score_ - scores.mean())*100:+.1f}%  (tuned vs default)")



# ── Confusion matrix: real vs predicted (P/E/G) ───────────────────────────
from sklearn.metrics import confusion_matrix
import numpy as np

label_order  = ["HOME_TEAM", "DRAW", "AWAY_TEAM"]
label_short  = ["Win", "Draw", "Loss"]

cm = confusion_matrix(y_test, pred, labels=label_order)
cm_pct = cm.astype(float) / cm.sum(axis=1, keepdims=True) * 100

fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(cm_pct, cmap="Blues", vmin=0, vmax=100)
plt.colorbar(im, ax=ax, label="%")

ax.set_xticks(range(3)); ax.set_xticklabels(label_short, fontsize=13)
ax.set_yticks(range(3)); ax.set_yticklabels(label_short, fontsize=13)
ax.set_xlabel("Predicted", fontsize=11)
ax.set_ylabel("Real", fontsize=11)
ax.set_title("Confusion Matrix — Real vs Predicted", fontsize=12)

for i in range(3):
    for j in range(3):
        ax.text(j, i, f"{cm[i,j]}\n({cm_pct[i,j]:.0f}%)",
                ha="center", va="center", fontsize=10,
                color="white" if cm_pct[i, j] > 55 else "black")

plt.tight_layout()
plt.show()

# ── Feature correlation matrix ────────────────────────────────────────────
corr = df_train[FEATURES].corr()

fig, ax = plt.subplots(figsize=(11, 9))
im2 = ax.imshow(corr.values, cmap="coolwarm", vmin=-1, vmax=1)
plt.colorbar(im2, ax=ax)

ax.set_xticks(range(len(FEATURES))); ax.set_xticklabels(FEATURES, rotation=45, ha="right", fontsize=8)
ax.set_yticks(range(len(FEATURES))); ax.set_yticklabels(FEATURES, fontsize=8)
ax.set_title("Feature Correlation Matrix", fontsize=12)

for i in range(len(FEATURES)):
    for j in range(len(FEATURES)):
        ax.text(j, i, f"{corr.values[i,j]:.2f}", ha="center", va="center", fontsize=6,
                color="white" if abs(corr.values[i,j]) > 0.6 else "black")

plt.tight_layout()
plt.show()

# ── ROC Curve (One-vs-Rest) ───────────────────────────────────────────────
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize

y_test_bin = label_binarize(y_test, classes=label_order)
y_proba    = model.predict_proba(X_test_scaled)
col_order  = [list(model.classes_).index(c) for c in label_order]
y_proba    = y_proba[:, col_order]

roc_colors = ["#4e9af1", "#f1c94e", "#f1674e"]
roc_labels = ["Home win", "Draw", "Away win"]

plt.figure(figsize=(8, 6))
for i, (color, lbl) in enumerate(zip(roc_colors, roc_labels)):
    fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_proba[:, i])
    plt.plot(fpr, tpr, color=color, lw=2, label=f"{lbl}  AUC = {auc(fpr, tpr):.2f}")

plt.plot([0, 1], [0, 1], "k--", lw=1)
plt.xlim([0, 1]); plt.ylim([0, 1.02])
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve — One-vs-Rest (SVM)")
plt.legend(loc="lower right")
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
