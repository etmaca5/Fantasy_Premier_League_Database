-- Setup file for Fantasy Premier League database

-- Clean up old tables by dropping preexisting tables
DROP TABLE IF EXISTS fpl_team_players;
DROP TABLE IF EXISTS matchweek;
DROP TABLE IF EXISTS fpl_team;
DROP TABLE IF EXISTS player;
DROP TABLE IF EXISTS user;


-- Stores user information unqiuely identified by a user_id, which is
-- auto created for each user
CREATE TABLE user (
    user_id         SERIAL          PRIMARY KEY,
    user_email      VARCHAR(50)     NOT NULL,
    username        VARCHAR(20)     NOT NULL
    -- password not stored for security
);


-- Stores player information
CREATE TABLE player (
    player_id       SMALLINT,
    player_name     VARCHAR(50)   NOT NULL,
    team_name       VARCHAR(20)       NOT NULL,
    -- Player's position (GK, DEF, MID, or FWD)
    position        VARCHAR(3)       NOT NULL,
    -- Cost of the player for FPL
    player_value    SMALLINT NOT NULL,
    total_points    INT        DEFAULT 0,
    PRIMARY KEY (player_id)
);


-- Stores team information for the fantasy team (the team managed by a user)
CREATE TABLE fpl_team (
    fpl_team_name   VARCHAR(20),
    user_id         BIGINT UNSIGNED,
    points          SMALLINT   DEFAULT 0,
    fpl_team_value  SMALLINT   NOT NULL,
    PRIMARY KEY (fpl_team_name, user_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Stores the players that each FPL team owns
-- Multiple FPL teams can own the same player
CREATE TABLE fpl_team_players (
    fpl_team_name   VARCHAR(20),
    player_id       SMALLINT,
    user_id        BIGINT UNSIGNED,
    PRIMARY KEY (fpl_team_name, player_id, user_id),
    FOREIGN KEY (fpl_team_name) REFERENCES fpl_team(fpl_team_name)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (player_id) REFERENCES player(player_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Stores matchweek information, the statistics for all of the players during
-- a single matchweek (from their respectives matches)
CREATE TABLE matchweek (
    player_id       SMALLINT,
    matchweek       TINYINT,
	goals           TINYINT     NOT NULL,
	assists         TINYINT     NOT NULL,
    -- 1 if the player's team did not concede that week (default 0)
	clean_sheets    TINYINT     DEFAULT 0,
	minutes_played  SMALLINT    NOT NULL,
    -- FPL points accumulated during the match
	points          SMALLINT    NOT NULL,
    PRIMARY KEY (matchweek, player_id),
    FOREIGN KEY (player_id) REFERENCES player(player_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Adding an index to the player table
-- Likely will be doing many searches for player by their value (sorting by
-- value, checking if a user can buy a player for their team, selling players)
CREATE INDEX idx_player_value ON player
  (player_value);