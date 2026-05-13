# WhoWillWin

A La Liga match prediction web app. It fetches historical match data, trains a machine learning model on it, and serves win probability predictions to a React frontend.

---

## Project Structure

```
whowillwin/
├── Predictor/          # Python: data ingestion + ML model + prediction API
│   ├── ingest.py       # Fetches data from football-data.org and populates the DB
│   ├── api.py          # FastAPI server — serves predictions to the frontend
│   ├── matchpredictor.py  # Standalone analysis/EDA script (not part of the server)
│   └── db.py           # DB connection helper
├── Backend/            # Go/Java backend — auth, users, match data endpoints
└── Frontend/
    └── whowillwin/     # React + TypeScript (Vite)
        └── src/
            ├── App.tsx
            ├── Matches.tsx
            ├── hooks/useMatches.ts
            ├── services/
            │   ├── api.ts          # Generic fetch wrapper
            │   ├── matchService.ts # Calls both backend and predictor API
            │   └── authService.ts  # Login / register / JWT
            └── types/prediction.ts
```

---

## How It Works

### 1. Data Ingestion (`ingest.py`)

Run once (or re-run safely — all inserts are idempotent):

```bash
cd Predictor
python ingest.py           # full run including per-match details
python ingest.py --no-details  # skip per-match details (much faster)
```

**What it does, in order:**

| Phase | Function | What it fetches |
|---|---|---|
| 1a | `ingest_teams` | All La Liga teams (names, crests, coaches) |
| 1b | `ingest_squads` | Player rosters for each season |
| 1c | `ingest_season` | All matches per season (scores, dates, status). Skips API call if season already in DB. |
| 2  | `ingest_match_details` | Per-match: goals, bookings, substitutions, penalties, lineups, stats. Skips matches already ingested (checks `match_stats`). |
| —  | `compute_standings` | Builds the standings table from match results (no extra API calls) |
| —  | `compute_h2h` | Builds head-to-head records from match results (no extra API calls) |

> **Rate limit:** The free tier of football-data.org allows 10 requests/min. The script sleeps 7 seconds between calls. Phase 2 across 3 seasons (~1100 matches) takes ~2 hours.

> **Free tier limitation:** Goals, lineups, bookings, substitutions, and penalties are not returned by the free tier API — those tables will remain empty.

---

### 2. ML Model (`api.py`)

The FastAPI server loads on startup and trains a **Random Forest classifier** in memory. It never writes to the DB — it only reads.

**Feature engineering** (all computed from past data only — no future leakage):

| Feature | Description |
|---|---|
| `home_avg_goals` / `away_avg_goals` | Average goals scored per game so far |
| `home_form5` / `away_form5` | Win rate over last 5 games |
| `home_win_rate_weighted` / `away_win_rate_weighted` | Overall win rate, scaled by games played (low confidence early in season) |
| `home_points` / `away_points` | League points before this match |
| `home_position` / `away_position` | Table position before this match |
| `home_goal_diff` / `away_goal_diff` | Goal difference before this match |
| `h2h_home_wins` / `h2h_away_wins` / `h2h_draws` / `h2h_avg_goals` | All-time head-to-head record between the two teams |
| `matchday` | How far into the season the match is |

**Training:** Only completed matches (`winner IS NOT NULL`) are used. The model outputs three probabilities that sum to 100%: home win, draw, away win.

**API endpoints:**

- `GET /future-predictions` — predictions for all unplayed matches in bulk
- `GET /predict?homeTeamId=X&awayTeamId=Y&matchday=N` — prediction for any specific matchup

---

### 3. Frontend (`Matches.tsx` + `useMatches.ts`)

The main view lets the user browse La Liga seasons, matchdays, and matches.

**Data flow:**

```
useMatches hook
  ├── getSeasons()        → backend API → season list → auto-selects current
  ├── getMatches()        → backend API → all matches for selected season
  └── selectMatchday()    → filters matches client-side

Matches component
  ├── useSquad()          → backend API → player list for selected match's teams
  └── getFuturePredictions() → predictor API (port 8000) → win % for all upcoming matches
```

**Prediction display:** When a future match is selected, the component looks up its prediction from the pre-fetched `futurePredictions` array by matching `homeTeamId` + `awayTeamId`.

---

## Running Locally

**Prerequisites:** PostgreSQL running on `localhost:5432`, Python 3.11+, Node 18+.

### Database

Run the schema once:
```bash
psql -U postgres -d postgres -f Backend/whowillwin/db/db.sql
```

### Predictor API

```bash
cd Predictor
pip install fastapi uvicorn sqlalchemy psycopg2 scikit-learn pandas requests
python ingest.py --no-details   # populate DB first
uvicorn api:app --port 8000
```

### Frontend

```bash
cd Frontend/whowillwin
npm install
npm run dev   # runs on http://localhost:5173
```

### Backend

See `Backend/` for the Go/Java service running on port `5081`.

---

## Environment

| Service | Port | Notes |
|---|---|---|
| Predictor API | 8000 | FastAPI, started with uvicorn |
| Backend API | 5081 | Auth, matches, teams |
| Frontend | 5173 | Vite dev server |
| PostgreSQL | 5432 | Schema: `whowillwin` |
