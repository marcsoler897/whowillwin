use whowillwin;

CREATE SCHEMA IF NOT EXISTS whowillwin;

CREATE TABLE whowillwin.teams (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE whowillwin.users (
    id UUID PRIMARY KEY,
    prefteam_id UUID NOT NULL,
    name VARCHAR(32) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    salt VARCHAR(8) NOT NULL,
    CONSTRAINT fk_user_team FOREIGN KEY (prefteam_id)
        REFERENCES whowillwin.teams(id)
); 

DROP TABLE whowillwin.users;