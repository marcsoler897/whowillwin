DROP SCHEMA IF EXISTS whowillwin CASCADE;
CREATE SCHEMA whowillwin;

CREATE TABLE whowillwin.teams (
    id uuid PRIMARY KEY,
    api_id int UNIQUE NOT NULL,
    name varchar(100) NOT NULL,
    short_name varchar(50),
    tla varchar(5),
    crest varchar(255),
    coach_name varchar(100)
);

CREATE TABLE whowillwin.users (
    id uuid PRIMARY KEY,
    prefteam_id uuid NOT NULL,
    name varchar(32) NOT NULL,
    email varchar(255) NOT NULL UNIQUE,
    password varchar(255) NOT NULL,
    salt varchar(8) NOT NULL,
    CONSTRAINT fk_user_team FOREIGN KEY (prefteam_id)
        REFERENCES whowillwin.teams(id)
);

CREATE TABLE whowillwin.roles (
    id uuid PRIMARY KEY,
    name varchar(50) NOT NULL
);

CREATE TABLE whowillwin.userroles (
    id uuid PRIMARY KEY,
    user_id uuid NOT NULL,
    role_id uuid NOT NULL,
    CONSTRAINT fk_userroles_users FOREIGN KEY (user_id)
        REFERENCES whowillwin.users(id),
    CONSTRAINT fk_userroles_roles FOREIGN KEY (role_id)
        REFERENCES whowillwin.roles(id),
    CONSTRAINT uq_userroles UNIQUE (user_id, role_id)
);

CREATE TABLE whowillwin.players (
    id uuid PRIMARY KEY,
    api_id int UNIQUE,
    name varchar(100) NOT NULL,
    first_name varchar(100),
    last_name varchar(100),
    date_of_birth date,
    nationality varchar(100),
    position varchar(50),
    shirt_number int,
    team_id uuid,
    contract_start varchar(10),
    contract_until varchar(10),
    CONSTRAINT fk_player_team FOREIGN KEY (team_id)
        REFERENCES whowillwin.teams(id)
);

CREATE TABLE whowillwin.matches (
    id uuid PRIMARY KEY,
    api_id int UNIQUE,
    home_team_id uuid NOT NULL,
    away_team_id uuid NOT NULL,
    utc_date timestamptz,
    status varchar(20),
    matchday int,
    season int,
    stage varchar(50),
    home_goals int,
    away_goals int,
    home_goals_ht int,
    away_goals_ht int,
    winner varchar(15),
    duration varchar(20),
    CONSTRAINT fk_match_home FOREIGN KEY (home_team_id)
        REFERENCES whowillwin.teams(id),
    CONSTRAINT fk_match_away FOREIGN KEY (away_team_id)
        REFERENCES whowillwin.teams(id)
);

CREATE TABLE whowillwin.match_stats (
    id uuid PRIMARY KEY,
    match_id uuid NOT NULL,
    team_id uuid NOT NULL,
    possession int,
    shots int,
    shots_on_goal int,
    shots_off_goal int,
    corners int,
    fouls int,
    offsides int,
    saves int,
    throw_ins int,
    free_kicks int,
    goal_kicks int,
    yellow_cards int,
    yellow_red_cards int,
    red_cards int,
    CONSTRAINT fk_stats_match FOREIGN KEY (match_id)
        REFERENCES whowillwin.matches(id),
    CONSTRAINT fk_stats_team FOREIGN KEY (team_id)
        REFERENCES whowillwin.teams(id),
    CONSTRAINT uq_stats UNIQUE (match_id, team_id)
);

CREATE TABLE whowillwin.goals (
    id uuid PRIMARY KEY,
    match_id uuid NOT NULL,
    team_id uuid,
    scorer_id uuid,
    assist_id uuid,
    minute int,
    injury_time int,
    type varchar(20),
    home_score_at_time int,
    away_score_at_time int,
    CONSTRAINT fk_goal_match FOREIGN KEY (match_id)
        REFERENCES whowillwin.matches(id),
    CONSTRAINT fk_goal_team FOREIGN KEY (team_id)
        REFERENCES whowillwin.teams(id),
    CONSTRAINT fk_goal_scorer FOREIGN KEY (scorer_id)
        REFERENCES whowillwin.players(id),
    CONSTRAINT fk_goal_assist FOREIGN KEY (assist_id)
        REFERENCES whowillwin.players(id)
);

CREATE TABLE whowillwin.bookings (
    id uuid PRIMARY KEY,
    match_id uuid NOT NULL,
    team_id uuid,
    player_id uuid,
    minute int,
    card varchar(20),
    CONSTRAINT fk_booking_match FOREIGN KEY (match_id)
        REFERENCES whowillwin.matches(id),
    CONSTRAINT fk_booking_team FOREIGN KEY (team_id)
        REFERENCES whowillwin.teams(id),
    CONSTRAINT fk_booking_player FOREIGN KEY (player_id)
        REFERENCES whowillwin.players(id)
);

CREATE TABLE whowillwin.substitutions (
    id uuid PRIMARY KEY,
    match_id uuid NOT NULL,
    team_id uuid,
    player_out_id uuid,
    player_in_id uuid,
    minute int,
    CONSTRAINT fk_sub_match FOREIGN KEY (match_id)
        REFERENCES whowillwin.matches(id),
    CONSTRAINT fk_sub_team FOREIGN KEY (team_id)
        REFERENCES whowillwin.teams(id),
    CONSTRAINT fk_sub_out FOREIGN KEY (player_out_id)
        REFERENCES whowillwin.players(id),
    CONSTRAINT fk_sub_in FOREIGN KEY (player_in_id)
        REFERENCES whowillwin.players(id)
);

CREATE TABLE whowillwin.penalties (
    id uuid PRIMARY KEY,
    match_id uuid NOT NULL,
    team_id uuid,
    player_id uuid,
    scored boolean NOT NULL,
    CONSTRAINT fk_pen_match FOREIGN KEY (match_id)
        REFERENCES whowillwin.matches(id),
    CONSTRAINT fk_pen_team FOREIGN KEY (team_id)
        REFERENCES whowillwin.teams(id),
    CONSTRAINT fk_pen_player FOREIGN KEY (player_id)
        REFERENCES whowillwin.players(id)
);

CREATE TABLE whowillwin.lineups (
    id uuid PRIMARY KEY,
    match_id uuid NOT NULL,
    team_id uuid NOT NULL,
    player_id uuid NOT NULL,
    position varchar(50),
    shirt_number int,
    type varchar(10),
    CONSTRAINT fk_lineup_match FOREIGN KEY (match_id)
        REFERENCES whowillwin.matches(id),
    CONSTRAINT fk_lineup_team FOREIGN KEY (team_id)
        REFERENCES whowillwin.teams(id),
    CONSTRAINT fk_lineup_player FOREIGN KEY (player_id)
        REFERENCES whowillwin.players(id),
    CONSTRAINT uq_lineup UNIQUE (match_id, player_id, type)
);

-- season column required: matchday 1 of 2022 and matchday 1 of 2023 are different rows
CREATE TABLE whowillwin.standings (
    id uuid PRIMARY KEY,
    team_id uuid NOT NULL,
    season int NOT NULL,
    matchday int NOT NULL,
    type varchar(10) NOT NULL,
    position int,
    played int,
    won int,
    drawn int,
    lost int,
    goals_for int,
    goals_against int,
    goal_diff int,
    points int,
    form varchar(50),
    CONSTRAINT fk_standing_team FOREIGN KEY (team_id)
        REFERENCES whowillwin.teams(id),
    CONSTRAINT uq_standing UNIQUE (team_id, season, matchday, type)
);

CREATE TABLE whowillwin.head_to_head (
    id uuid PRIMARY KEY,
    team1_id uuid NOT NULL,
    team2_id uuid NOT NULL,
    total_matches int,
    team1_wins int,
    draws int,
    team2_wins int,
    total_goals int,
    last_updated timestamptz,
    CONSTRAINT fk_h2h_team1 FOREIGN KEY (team1_id)
        REFERENCES whowillwin.teams(id),
    CONSTRAINT fk_h2h_team2 FOREIGN KEY (team2_id)
        REFERENCES whowillwin.teams(id),
    CONSTRAINT uq_h2h UNIQUE (team1_id, team2_id)
);

INSERT INTO whowillwin.roles (id, name) VALUES
('11111111-1111-1111-1111-111111111111', 'Admin'),
('22222222-2222-2222-2222-222222222222', 'User');

INSERT INTO whowillwin.userroles (id, user_id, role_id) VALUES
(gen_random_uuid(), '4040f836-ef78-4d0b-9f48-1c5ab3992673', '11111111-1111-1111-1111-111111111111'),
(gen_random_uuid(), '4cf8204c-a2dc-4cb8-89ca-d496e5de754d', '22222222-2222-2222-2222-222222222222');