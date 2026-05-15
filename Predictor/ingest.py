"""
La Liga (competition 2014) ingestion from football-data.org v4.

Run once (or re-run; all inserts are idempotent via ON CONFLICT):
    python ingest.py

Phase 1 — teams, squads, matches + goals  (~10 API calls per season, fast)
Phase 2 — per-match details: stats, lineups, bookings, subs  (1 call / match)
           Skip with --no-details if you just want predictions working fast.

Rate limit: free tier = 10 req/min  →  7-second sleep between calls.
"""

# import argparse
import time
import uuid
# from collections import defaultdict

import requests
# from psycopg2.extras import execute_values

from db import get_connection

# ── config ────────────────────────────────────────────────────────────────────
API_KEY        = "dfa2c7aa37eb4a7e893d6bf5b25018a1"
BASE_URL       = "https://api.football-data.org/v4"
COMPETITION_ID = 2014
SEASONS        = [2023, 2024, 2025]
CALL_DELAY     = 7      # seconds between calls (10/min limit + 1 s buffer)

HEADERS = {"X-Auth-Token": API_KEY}


# ── low-level helpers ─────────────────────────────────────────────────────────

def api_get(path: str, params: dict = None, extra_headers: dict = None):
    headers = dict(HEADERS)
    if extra_headers:
        headers.update(extra_headers)
    url = f"{BASE_URL}/{path}"
    for _ in range(3):
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        if resp.status_code == 429:
            wait = int(resp.headers.get("X-RequestCounter-Reset", 65))
            print(f"  [rate limit] waiting {wait}s …")
            time.sleep(wait + 1)
            continue
        if resp.status_code in (403, 404):
            print(f"  [{resp.status_code}] {url} — skipping")
            return None
        resp.raise_for_status()
        time.sleep(CALL_DELAY)
        return resp.json()
    return None


def _team_uuid(cur, api_id: int):
    cur.execute("SELECT id FROM whowillwin.teams WHERE api_id = %s", (api_id,))
    row = cur.fetchone()
    return row[0] if row else None


# def _player_uuid(cur, api_id: int):
#     if not api_id:
#         return None
#     cur.execute("SELECT id FROM whowillwin.players WHERE api_id = %s", (api_id,))
#     row = cur.fetchone()
#     return row[0] if row else None


# def _ensure_player(cur, p: dict, team_uuid) -> str | None:
#     """Return the player's internal UUID, inserting a minimal row if missing."""
#     if not p or not p.get("id"):
#         return None
#     pid = _player_uuid(cur, p["id"])
#     if pid:
#         return pid
#     new_id = str(uuid.uuid4())
#     cur.execute(
#         """
#         INSERT INTO whowillwin.players (id, api_id, name, team_id)
#         VALUES (%s, %s, %s, %s)
#         ON CONFLICT (api_id) DO NOTHING
#         """,
#         (new_id, p["id"], p.get("name", ""), str(team_uuid) if team_uuid else None),
#     )
#     return _player_uuid(cur, p["id"]) or new_id


# def _ensure_team(cur, td: dict):
#     """Insert a minimal team row if it doesn't exist yet."""
#     cur.execute(
#         """
#         INSERT INTO whowillwin.teams (id, api_id, name, short_name, tla, crest)
#         VALUES (%s, %s, %s, %s, %s, %s)
#         ON CONFLICT (api_id) DO NOTHING
#         """,
#         (str(uuid.uuid4()), td["id"], td["name"],
#          td.get("shortName"), td.get("tla"), td.get("crest")),
#     )


# ── phase 1a: teams ───────────────────────────────────────────────────────────

# def ingest_teams(conn):
#     print("Fetching competition teams …")
#     data = api_get(f"competitions/{COMPETITION_ID}/teams")
#     if not data:
#         print("  no data — aborting")
#         return
#
#     cur = conn.cursor()
#     for team in data.get("teams", []):
#         coach = team.get("coach") or {}
#         cur.execute(
#             """
#             INSERT INTO whowillwin.teams
#                 (id, api_id, name, short_name, tla, crest, coach_name)
#             VALUES (%s, %s, %s, %s, %s, %s, %s)
#             ON CONFLICT (api_id) DO UPDATE SET
#                 name       = EXCLUDED.name,
#                 short_name = EXCLUDED.short_name,
#                 tla        = EXCLUDED.tla,
#                 crest      = EXCLUDED.crest,
#                 coach_name = EXCLUDED.coach_name
#             """,
#             (
#                 str(uuid.uuid4()),
#                 team["id"],
#                 team["name"],
#                 team.get("shortName"),
#                 team.get("tla"),
#                 team.get("crest"),
#                 coach.get("name") if isinstance(coach, dict) else None,
#             ),
#         )
#     conn.commit()
#     cur.close()
#
#     cur = conn.cursor()
#     cur.execute("SELECT COUNT(*) FROM whowillwin.teams")
#     print(f"  {cur.fetchone()[0]} teams in db.")
#     cur.close()


# ── phase 1b: squads / players ────────────────────────────────────────────────

# def ingest_squads(conn):
#     for season in SEASONS:
#         print(f"Fetching squads for season {season} …", end=" ", flush=True)
#         data = api_get(
#             f"competitions/{COMPETITION_ID}/teams",
#             params={"season": season},
#         )
#         if not data:
#             print("no data.")
#             continue
#
#         cur = conn.cursor()
#         player_count = 0
#         for team in data.get("teams", []):
#             t_api_id = team["id"]
#             cur.execute("SELECT id FROM whowillwin.teams WHERE api_id = %s", (t_api_id,))
#             row = cur.fetchone()
#             if not row:
#                 continue
#             t_uuid = row[0]
#
#             coach = team.get("coach") or {}
#             if isinstance(coach, dict) and coach.get("name"):
#                 cur.execute(
#                     "UPDATE whowillwin.teams SET coach_name = %s WHERE id = %s",
#                     (coach["name"], str(t_uuid)),
#                 )
#
#             for p in team.get("squad", []):
#                 contract = p.get("contract") or {}
#                 cur.execute(
#                     """
#                     INSERT INTO whowillwin.players
#                         (id, api_id, name, first_name, last_name, date_of_birth,
#                          nationality, position, shirt_number, team_id,
#                          contract_start, contract_until)
#                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#                     ON CONFLICT (api_id) DO UPDATE SET
#                         name           = EXCLUDED.name,
#                         position       = EXCLUDED.position,
#                         shirt_number   = EXCLUDED.shirt_number,
#                         team_id        = EXCLUDED.team_id,
#                         contract_start = EXCLUDED.contract_start,
#                         contract_until = EXCLUDED.contract_until
#                     """,
#                     (
#                         str(uuid.uuid4()),
#                         p["id"],
#                         p.get("name", ""),
#                         p.get("firstName"),
#                         p.get("lastName") or p.get("name", ""),
#                         p.get("dateOfBirth"),
#                         p.get("nationality"),
#                         p.get("position"),
#                         p.get("shirtNumber"),
#                         str(t_uuid),
#                         contract.get("start") if isinstance(contract, dict) else None,
#                         contract.get("until") if isinstance(contract, dict) else None,
#                     ),
#                 )
#                 player_count += 1
#
#         conn.commit()
#         cur.close()
#         print(f"{player_count} players.")

# ── phase 1c: matches + goals (bulk) ─────────────────────────────────────────

# def ingest_season(conn, season: int) -> list[tuple]:
#     """
#     Fetch all matches for a season.
#     Returns [(internal_uuid_str, api_id)] for finished matches (phase 2 input).
#     Skips the API call if matches for this season are already in the DB.
#     """
#     cur = conn.cursor()
#     cur.execute(
#         "SELECT COUNT(*) FROM whowillwin.matches WHERE season = %s", (season,)
#     )
#     existing = cur.fetchone()[0]
#     cur.close()
#
#     if existing:
#         print(f"Season {season}: {existing} matches already in DB, loading from DB …", end=" ", flush=True)
#         cur = conn.cursor()
#         cur.execute(
#             "SELECT id, api_id FROM whowillwin.matches WHERE season = %s AND status = 'FINISHED'",
#             (season,),
#         )
#         pairs = [(str(r[0]), r[1]) for r in cur.fetchall()]
#         cur.close()
#         print(f"{len(pairs)} finished.")
#         return pairs
#
#     print(f"Season {season}: fetching matches from API …", end=" ", flush=True)
#     data = api_get(
#         f"competitions/{COMPETITION_ID}/matches",
#         params={"season": season},
#     )
#     if not data:
#         print("no data.")
#         return []
#
#     cur = conn.cursor()
#     inserted        = 0
#     finished_pairs: list[tuple] = []
#
#     for m in data.get("matches", []):
#         for td in (m["homeTeam"], m["awayTeam"]):
#             _ensure_team(cur, td)
#
#         h_uuid = _team_uuid(cur, m["homeTeam"]["id"])
#         a_uuid = _team_uuid(cur, m["awayTeam"]["id"])
#         if not h_uuid or not a_uuid:
#             continue
#
#         finished = m["status"] == "FINISHED"
#         score    = m.get("score", {})
#         ft       = score.get("fullTime", {})
#         ht_s     = score.get("halfTime", {})
#         m_uuid   = str(uuid.uuid4())
#
#         cur.execute(
#             """
#             INSERT INTO whowillwin.matches
#                 (id, api_id, home_team_id, away_team_id, utc_date, status,
#                  matchday, season, stage,
#                  home_goals, away_goals, home_goals_ht, away_goals_ht,
#                  winner, duration)
#             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
#             ON CONFLICT (api_id) DO UPDATE SET
#                 status        = EXCLUDED.status,
#                 home_goals    = EXCLUDED.home_goals,
#                 away_goals    = EXCLUDED.away_goals,
#                 home_goals_ht = EXCLUDED.home_goals_ht,
#                 away_goals_ht = EXCLUDED.away_goals_ht,
#                 winner        = EXCLUDED.winner,
#                 duration      = EXCLUDED.duration
#             RETURNING id
#             """,
#             (
#                 m_uuid, m["id"], str(h_uuid), str(a_uuid),
#                 m["utcDate"], m["status"],
#                 m.get("matchday"), season,
#                 m.get("stage"),
#                 ft.get("home") if finished else None,
#                 ft.get("away") if finished else None,
#                 ht_s.get("home") if finished else None,
#                 ht_s.get("away") if finished else None,
#                 score.get("winner"),
#                 score.get("duration"),
#             ),
#         )
#         row = cur.fetchone()
#         db_uuid = str(row[0]) if row else None
#         inserted += 1
#
#         if finished and db_uuid:
#             finished_pairs.append((db_uuid, m["id"]))
#
#     conn.commit()
#     cur.close()
#     print(f"{inserted} matches.")
#     return finished_pairs


# ── phase 2: individual match details ────────────────────────────────────────

# def _stat(stats: list, key: str):
#     for s in stats:
#         if s.get("type") == key:
#             v = s.get("value")
#             if v is None:
#                 return None
#             try:
#                 return int(str(v).rstrip("%"))
#             except ValueError:
#                 return None
#     return None


# def ingest_match_details(conn, db_uuid: str, api_id: int):
#     data = api_get(f"matches/{api_id}")
#     if not data:
#         return
#
#     cur = conn.cursor()
#
#     # ── goals ────────────────────────────────────────────────────────────────
#     # delete existing goals for this match so re-runs don't duplicate
#     cur.execute("DELETE FROM whowillwin.goals WHERE match_id = %s", (db_uuid,))
#     for g in data.get("goals", []):
#         scorer = g.get("scorer") or {}
#         assist = g.get("assist") or {}
#         g_team = g.get("team")   or {}
#         scorer_uuid = None
#         assist_uuid = None
#         if scorer.get("id"):
#             scorer_uuid = _player_uuid(cur, scorer["id"])
#             if not scorer_uuid:
#                 scorer_uuid = _ensure_player(cur, scorer, _team_uuid(cur, g_team.get("id")))
#         if assist.get("id"):
#             assist_uuid = _player_uuid(cur, assist["id"])
#             if not assist_uuid:
#                 assist_uuid = _ensure_player(cur, assist, _team_uuid(cur, g_team.get("id")))
#         cur.execute(
#             """
#             INSERT INTO whowillwin.goals
#                 (id, match_id, team_id, scorer_id, assist_id,
#                  minute, injury_time, type,
#                  home_score_at_time, away_score_at_time)
#             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
#             """,
#             (
#                 str(uuid.uuid4()), db_uuid,
#                 str(_team_uuid(cur, g_team["id"])) if g_team.get("id") else None,
#                 str(scorer_uuid) if scorer_uuid else None,
#                 str(assist_uuid) if assist_uuid else None,
#                 g.get("minute"), g.get("injuryTime"), g.get("type"),
#                 g.get("homeScore"), g.get("awayScore"),
#             ),
#         )
#
#     # ── bookings ──────────────────────────────────────────────────────────────
#     cur.execute("DELETE FROM whowillwin.bookings WHERE match_id = %s", (db_uuid,))
#     for b in data.get("bookings", []):
#         p = b.get("player") or {}
#         t = b.get("team")   or {}
#         t_uuid = _team_uuid(cur, t["id"]) if t.get("id") else None
#         p_uuid = None
#         if p.get("id"):
#             p_uuid = _player_uuid(cur, p["id"])
#             if not p_uuid:
#                 p_uuid = _ensure_player(cur, p, t_uuid)
#         cur.execute(
#             "INSERT INTO whowillwin.bookings (id,match_id,team_id,player_id,minute,card)"
#             " VALUES (%s,%s,%s,%s,%s,%s)",
#             (
#                 str(uuid.uuid4()), db_uuid,
#                 str(t_uuid) if t_uuid else None,
#                 str(p_uuid) if p_uuid else None,
#                 b.get("minute"), b.get("card"),
#             ),
#         )
#
#     # ── substitutions ─────────────────────────────────────────────────────────
#     cur.execute("DELETE FROM whowillwin.substitutions WHERE match_id = %s", (db_uuid,))
#     for s in data.get("substitutions", []):
#         t     = s.get("team")      or {}
#         p_out = s.get("playerOut") or {}
#         p_in  = s.get("playerIn")  or {}
#         t_uuid = _team_uuid(cur, t["id"]) if t.get("id") else None
#         out_uuid = None
#         in_uuid  = None
#         if p_out.get("id"):
#             out_uuid = _player_uuid(cur, p_out["id"])
#             if not out_uuid:
#                 out_uuid = _ensure_player(cur, p_out, t_uuid)
#         if p_in.get("id"):
#             in_uuid = _player_uuid(cur, p_in["id"])
#             if not in_uuid:
#                 in_uuid = _ensure_player(cur, p_in, t_uuid)
#         cur.execute(
#             "INSERT INTO whowillwin.substitutions"
#             " (id,match_id,team_id,player_out_id,player_in_id,minute)"
#             " VALUES (%s,%s,%s,%s,%s,%s)",
#             (
#                 str(uuid.uuid4()), db_uuid,
#                 str(t_uuid)   if t_uuid   else None,
#                 str(out_uuid) if out_uuid else None,
#                 str(in_uuid)  if in_uuid  else None,
#                 s.get("minute"),
#             ),
#         )
#
#     # ── penalties ─────────────────────────────────────────────────────────────
#     cur.execute("DELETE FROM whowillwin.penalties WHERE match_id = %s", (db_uuid,))
#     for pen in data.get("penalties", []):
#         p = pen.get("player") or {}
#         t = pen.get("team")   or {}
#         t_uuid = _team_uuid(cur, t["id"]) if t.get("id") else None
#         p_uuid = None
#         if p.get("id"):
#             p_uuid = _player_uuid(cur, p["id"])
#             if not p_uuid:
#                 p_uuid = _ensure_player(cur, p, t_uuid)
#         cur.execute(
#             "INSERT INTO whowillwin.penalties (id,match_id,team_id,player_id,scored)"
#             " VALUES (%s,%s,%s,%s,%s)",
#             (
#                 str(uuid.uuid4()), db_uuid,
#                 str(t_uuid) if t_uuid else None,
#                 str(p_uuid) if p_uuid else None,
#                 pen.get("scored", False),
#             ),
#         )
#
#     # ── lineups ───────────────────────────────────────────────────────────────
#     for side_key in ("homeTeam", "awayTeam"):
#         side   = data.get(side_key, {})
#         t_uuid = _team_uuid(cur, side.get("id"))
#         if not t_uuid:
#             continue
#         for ltype, players in (("LINEUP", side.get("lineup", [])),
#                                ("BENCH",  side.get("bench",  []))):
#             for p in players:
#                 pu = _ensure_player(cur, p, t_uuid)
#                 if not pu:
#                     continue
#                 cur.execute(
#                     """
#                     INSERT INTO whowillwin.lineups
#                         (id, match_id, team_id, player_id, position, shirt_number, type)
#                     VALUES (%s,%s,%s,%s,%s,%s,%s)
#                     ON CONFLICT (match_id, player_id, type) DO NOTHING
#                     """,
#                     (str(uuid.uuid4()), db_uuid, str(t_uuid), str(pu),
#                      p.get("position"), p.get("shirtNumber"), ltype),
#                 )
#
#     # ── match stats ───────────────────────────────────────────────────────────
#     cur.execute("SELECT COUNT(*) FROM whowillwin.match_stats WHERE match_id = %s", (db_uuid,))
#     if cur.fetchone()[0] == 0:
#         for side_key in ("homeTeam", "awayTeam"):
#             side   = data.get(side_key, {})
#             t_uuid = _team_uuid(cur, side.get("id"))
#             if not t_uuid:
#                 continue
#             stats = side.get("statistics") or []
#             cur.execute(
#                 """
#                 INSERT INTO whowillwin.match_stats
#                     (id, match_id, team_id,
#                      possession, shots, shots_on_goal, shots_off_goal,
#                      corners, fouls, offsides, saves,
#                      throw_ins, free_kicks, goal_kicks,
#                      yellow_cards, yellow_red_cards, red_cards)
#                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
#                 ON CONFLICT (match_id, team_id) DO UPDATE SET
#                     possession      = EXCLUDED.possession,
#                     shots           = EXCLUDED.shots,
#                     shots_on_goal   = EXCLUDED.shots_on_goal,
#                     shots_off_goal  = EXCLUDED.shots_off_goal,
#                     corners         = EXCLUDED.corners,
#                     fouls           = EXCLUDED.fouls,
#                     offsides        = EXCLUDED.offsides,
#                     saves           = EXCLUDED.saves,
#                     throw_ins       = EXCLUDED.throw_ins,
#                     free_kicks      = EXCLUDED.free_kicks,
#                     goal_kicks      = EXCLUDED.goal_kicks,
#                     yellow_cards    = EXCLUDED.yellow_cards,
#                     yellow_red_cards = EXCLUDED.yellow_red_cards,
#                     red_cards       = EXCLUDED.red_cards
#                 """,
#                 (
#                     str(uuid.uuid4()), db_uuid, str(t_uuid),
#                     _stat(stats, "BALL_POSSESSION"),
#                     _stat(stats, "TOTAL_SHOTS"),
#                     _stat(stats, "SHOTS_ON_GOAL"),
#                     _stat(stats, "SHOTS_OFF_GOAL"),
#                     _stat(stats, "CORNER_KICKS"),
#                     _stat(stats, "FOULS"),
#                     _stat(stats, "OFFSIDES"),
#                     _stat(stats, "GOALKEEPER_SAVES"),
#                     _stat(stats, "THROW_INS"),
#                     _stat(stats, "FREE_KICKS"),
#                     _stat(stats, "GOAL_KICKS"),
#                     _stat(stats, "YELLOW_CARDS"),
#                     _stat(stats, "YELLOW_RED_CARDS"),
#                     _stat(stats, "RED_CARDS"),
#                 ),
#             )
#
#     conn.commit()
#     cur.close()


# ── standings (computed from match results, no extra API calls) ───────────────

# def compute_standings(conn, season: int):
#     print(f"  Season {season} standings …", end=" ", flush=True)
#     cur = conn.cursor()
#     cur.execute(
#         """
#         SELECT matchday, home_team_id, away_team_id, home_goals, away_goals
#         FROM   whowillwin.matches
#         WHERE  season = %s AND status = 'FINISHED'
#           AND  matchday IS NOT NULL AND home_goals IS NOT NULL
#         ORDER  BY matchday, utc_date
#         """,
#         (season,),
#     )
#     rows = cur.fetchall()
#     cur.close()
#
#     if not rows:
#         print("no data.")
#         return
#
#     by_day   = defaultdict(list)
#     for row in rows:
#         by_day[row[0]].append(row)
#     max_day = max(by_day)
#
#     total  = defaultdict(lambda: dict(played=0, won=0, drawn=0, lost=0,
#                                       gf=0, ga=0, pts=0, form=[]))
#     home_s = defaultdict(lambda: dict(played=0, won=0, drawn=0, lost=0,
#                                       gf=0, ga=0, pts=0))
#     away_s = defaultdict(lambda: dict(played=0, won=0, drawn=0, lost=0,
#                                       gf=0, ga=0, pts=0))
#
#     standing_rows = []
#
#     for day in range(1, max_day + 1):
#         # update state with this day's results
#         for _, h_id, a_id, hg, ag in by_day.get(day, []):
#             if hg > ag:
#                 hp, ap, ho, ao = 3, 0, "W", "L"
#             elif hg == ag:
#                 hp, ap, ho, ao = 1, 1, "D", "D"
#             else:
#                 hp, ap, ho, ao = 0, 3, "L", "W"
#
#             for tid, pts, gf, ga, outcome in (
#                 (str(h_id), hp, hg, ag, ho),
#                 (str(a_id), ap, ag, hg, ao),
#             ):
#                 t = total[tid]
#                 t["played"] += 1; t["gf"] += gf; t["ga"] += ga; t["pts"] += pts
#                 if pts == 3:   t["won"]   += 1
#                 elif pts == 1: t["drawn"] += 1
#                 else:          t["lost"]  += 1
#                 t["form"].append(outcome)
#
#             for tid, pts, gf, ga, side_dict in (
#                 (str(h_id), hp, hg, ag, home_s),
#                 (str(a_id), ap, ag, hg, away_s),
#             ):
#                 s = side_dict[tid]
#                 s["played"] += 1; s["gf"] += gf; s["ga"] += ga; s["pts"] += pts
#                 if pts == 3:   s["won"]   += 1
#                 elif pts == 1: s["drawn"] += 1
#                 else:          s["lost"]  += 1
#
#         all_tids = list(total.keys())
#         if not all_tids:
#             continue
#
#         ranked = sorted(
#             all_tids,
#             key=lambda t: (total[t]["pts"],
#                            total[t]["gf"] - total[t]["ga"],
#                            total[t]["gf"]),
#             reverse=True,
#         )
#         pos_map = {t: i + 1 for i, t in enumerate(ranked)}
#
#         for tid in all_tids:
#             t = total[tid]; h = home_s[tid]; a = away_s[tid]
#             form_str = ",".join(t["form"][-5:])
#             standing_rows.extend([
#                 (str(uuid.uuid4()), tid, season, day, "TOTAL",
#                  pos_map[tid], t["played"], t["won"], t["drawn"], t["lost"],
#                  t["gf"], t["ga"], t["gf"] - t["ga"], t["pts"], form_str),
#                 (str(uuid.uuid4()), tid, season, day, "HOME",
#                  None, h["played"], h["won"], h["drawn"], h["lost"],
#                  h["gf"], h["ga"], h["gf"] - h["ga"], h["pts"], None),
#                 (str(uuid.uuid4()), tid, season, day, "AWAY",
#                  None, a["played"], a["won"], a["drawn"], a["lost"],
#                  a["gf"], a["ga"], a["gf"] - a["ga"], a["pts"], None),
#             ])
#
#     cur = conn.cursor()
#     execute_values(
#         cur,
#         """
#         INSERT INTO whowillwin.standings
#             (id, team_id, season, matchday, type, position,
#              played, won, drawn, lost,
#              goals_for, goals_against, goal_diff, points, form)
#         VALUES %s
#         ON CONFLICT (team_id, season, matchday, type) DO UPDATE SET
#             position      = EXCLUDED.position,
#             played        = EXCLUDED.played,
#             won           = EXCLUDED.won,
#             drawn         = EXCLUDED.drawn,
#             lost          = EXCLUDED.lost,
#             goals_for     = EXCLUDED.goals_for,
#             goals_against = EXCLUDED.goals_against,
#             goal_diff     = EXCLUDED.goal_diff,
#             points        = EXCLUDED.points,
#             form          = EXCLUDED.form
#         """,
#         standing_rows,
#     )
#     conn.commit()
#     cur.close()
#     print(f"{len(standing_rows)} rows.")


# ── head-to-head ──────────────────────────────────────────────────────────────

# def compute_h2h(conn):
#     print("Computing head-to-head …", end=" ", flush=True)
#     cur = conn.cursor()
#     cur.execute(
#         """
#         SELECT home_team_id, away_team_id, home_goals, away_goals
#         FROM   whowillwin.matches
#         WHERE  status = 'FINISHED' AND home_goals IS NOT NULL
#         ORDER  BY utc_date
#         """
#     )
#     rows = cur.fetchall()
#     cur.close()
#
#     h2h: dict = {}
#     for h_id, a_id, hg, ag in rows:
#         # canonical key: lexicographically smaller UUID string first
#         t1, t2 = (str(h_id), str(a_id)) if str(h_id) < str(a_id) else (str(a_id), str(h_id))
#         rec = h2h.setdefault((t1, t2), dict(total=0, t1_wins=0, draws=0, t2_wins=0, goals=0))
#         rec["total"] += 1
#         rec["goals"] += hg + ag
#         if hg == ag:
#             rec["draws"] += 1
#         elif (hg > ag and str(h_id) == t1) or (ag > hg and str(a_id) == t1):
#             rec["t1_wins"] += 1
#         else:
#             rec["t2_wins"] += 1
#
#     cur = conn.cursor()
#     for (t1, t2), rec in h2h.items():
#         cur.execute(
#             """
#             INSERT INTO whowillwin.head_to_head
#                 (id, team1_id, team2_id, total_matches,
#                  team1_wins, draws, team2_wins, total_goals, last_updated)
#             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NOW())
#             ON CONFLICT (team1_id, team2_id) DO UPDATE SET
#                 total_matches = EXCLUDED.total_matches,
#                 team1_wins    = EXCLUDED.team1_wins,
#                 draws         = EXCLUDED.draws,
#                 team2_wins    = EXCLUDED.team2_wins,
#                 total_goals   = EXCLUDED.total_goals,
#                 last_updated  = NOW()
#             """,
#             (str(uuid.uuid4()), t1, t2,
#              rec["total"], rec["t1_wins"], rec["draws"], rec["t2_wins"], rec["goals"]),
#         )
#     conn.commit()
#     cur.close()
#     print(f"{len(h2h)} pairs.")


# ── scorers table ─────────────────────────────────────────────────────────────

def create_scorers_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS whowillwin.scorers (
            id          uuid PRIMARY KEY,
            team_id     uuid NOT NULL,
            season      int  NOT NULL,
            goals       int  NOT NULL DEFAULT 0,
            assists     int  NOT NULL DEFAULT 0,
            penalties   int  NOT NULL DEFAULT 0,
            CONSTRAINT fk_scorer_team FOREIGN KEY (team_id)
                REFERENCES whowillwin.teams(id),
            CONSTRAINT uq_scorer UNIQUE (team_id, season)
        )
    """)
    conn.commit()
    cur.close()
    print("scorers table ready.")


def ingest_scorers(conn, season: int):
    print(f"Fetching scorers for season {season} …", end=" ", flush=True)
    data = api_get(f"competitions/{COMPETITION_ID}/scorers", params={"season": season, "limit": 100})
    if not data:
        print("no data.")
        return

    team_totals: dict = {}
    for entry in data.get("scorers", []):
        team = entry.get("team") or {}
        team_api_id = team.get("id")
        if not team_api_id:
            continue
        goals     = entry.get("goals") or 0
        assists   = entry.get("assists") or 0
        penalties = entry.get("penalties") or 0
        if team_api_id not in team_totals:
            team_totals[team_api_id] = {"goals": 0, "assists": 0, "penalties": 0}
        team_totals[team_api_id]["goals"]     += goals
        team_totals[team_api_id]["assists"]   += assists
        team_totals[team_api_id]["penalties"] += penalties

    cur = conn.cursor()
    inserted = 0
    for team_api_id, totals in team_totals.items():
        t_uuid = _team_uuid(cur, team_api_id)
        if not t_uuid:
            continue
        cur.execute("""
            INSERT INTO whowillwin.scorers (id, team_id, season, goals, assists, penalties)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (team_id, season) DO UPDATE SET
                goals     = EXCLUDED.goals,
                assists   = EXCLUDED.assists,
                penalties = EXCLUDED.penalties
        """, (str(uuid.uuid4()), str(t_uuid), season,
              totals["goals"], totals["assists"], totals["penalties"]))
        inserted += 1

    conn.commit()
    cur.close()
    print(f"{inserted} teams.")


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    conn = get_connection()

    # ── scorers (active) ──────────────────────────────────────────────────────
    create_scorers_table(conn)
    for season in SEASONS:
        ingest_scorers(conn, season)

    # # 1a — teams
    # ingest_teams(conn)

    # # 1b — squads / players
    # ingest_squads(conn)

    # # 1c — matches
    # all_finished: list[tuple] = []
    # for season in SEASONS:
    #     pairs = ingest_season(conn, season)
    #     all_finished.extend(pairs)

    # # 2 — per-match details
    # cur = conn.cursor()
    # cur.execute("SELECT DISTINCT match_id FROM whowillwin.goals")
    # done = {str(r[0]) for r in cur.fetchall()}
    # cur.close()
    # pending = [(db_uuid, m) for db_uuid, m in all_finished if db_uuid not in done]
    # for i, (db_uuid, api_id) in enumerate(pending, 1):
    #     if i % 20 == 0:
    #         print(f"  {i}/{len(pending)}")
    #     ingest_match_details(conn, db_uuid, api_id)

    # # standings
    # for season in SEASONS:
    #     compute_standings(conn, season)

    # # head-to-head
    # compute_h2h(conn)

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()