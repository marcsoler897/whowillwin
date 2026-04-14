CREATE SCHEMA IF NOT EXISTS whowillwin;

CREATE TABLE whowillwin.teams (
    id uuid PRIMARY KEY,
    name varchar(100) NOT NULL
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

CREATE TABLE whowillwin.matches_history (
    id           BIGINT PRIMARY KEY,
    season       INT NOT NULL,
    matchday     INT,
    utc_date     TIMESTAMP NOT NULL,
    home_team_id INT NOT NULL,
    home_team    VARCHAR(100) NOT NULL,
    away_team_id INT NOT NULL,
    away_team    VARCHAR(100) NOT NULL,
    home_goals   INT NOT NULL,
    away_goals   INT NOT NULL
);

CREATE TABLE whowillwin.team_elo (
    team_id   INT PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    elo       FLOAT NOT NULL DEFAULT 1500,
    matches   INT NOT NULL DEFAULT 0
);

INSERT INTO whowillwin.roles (id, name) VALUES
('11111111-1111-1111-1111-111111111111', 'Admin'),
('22222222-2222-2222-2222-222222222222', 'User');

INSERT INTO whowillwin.userroles (id, user_id, role_id) VALUES
(gen_random_uuid(), '4040f836-ef78-4d0b-9f48-1c5ab3992673', '11111111-1111-1111-1111-111111111111'),
(gen_random_uuid(), '4cf8204c-a2dc-4cb8-89ca-d496e5de754d', '22222222-2222-2222-2222-222222222222');