DROP PROCEDURE IF EXISTS sp_add_player;
DROP PROCEDURE IF EXISTS sp_remove_player;
DROP PROCEDURE IF EXISTS sp_add_team;
DROP FUNCTION IF EXISTS fn_get_player_value;
DROP FUNCTION IF EXISTS fn_check_player_team;
DROP TRIGGER IF EXISTS tr_increase_team_value;
DROP TRIGGER IF EXISTS tr_decrease_team_value;
-- This procedure inserts new team into fpl_team table, with certain starting value
DELIMITER !
CREATE PROCEDURE sp_add_team(
    fpl_team_name VARCHAR(20), 
    user_id BIGINT UNSIGNED, 
    starting_team_value SMALLINT
)
BEGIN
    INSERT INTO fpl_team
        VALUES (fpl_team_name, user_id, 0, starting_team_value);
END !
DELIMITER ;

-- procedure inserts new player into an fpl team
DELIMITER !
CREATE PROCEDURE sp_add_player(
    fpl_team   VARCHAR(20),
    player_id  SMALLINT,
    user_id    BIGINT UNSIGNED
)
BEGIN
    INSERT INTO fpl_team_players (fpl_team_name, player_id, user_id)
    VALUES (fpl_team, player_id, user_id);
END !
DELIMITER ;

-- procedure removes a player
DELIMITER !
CREATE PROCEDURE sp_remove_player(
    fpl_team      VARCHAR(20),
    player_id_remove     SMALLINT,
    user       BIGINT UNSIGNED
)
BEGIN
    DELETE FROM fpl_team_players
    WHERE fpl_team_name = fpl_team AND 
        user_id = user AND
        player_id = player_id_remove;
END !
DELIMITER ;

-- Function returns a player's value
DELIMITER !
CREATE FUNCTION fn_get_player_value(p_id SMALLINT)
RETURNS SMALLINT DETERMINISTIC
BEGIN
    DECLARE value SMALLINT;
    SELECT player_value INTO value
        FROM player
        WHERE player_id = p_id;
    RETURN value;
END !
DELIMITER ;

-- Checks if a player is in an FPL team
DELIMITER !
CREATE FUNCTION fn_check_player_team(
    team_name VARCHAR(20), 
    p_id SMALLINT, 
    u_id BIGINT UNSIGNED
)
RETURNS BOOLEAN DETERMINISTIC
BEGIN
    DECLARE is_in_team BOOLEAN;
    SELECT EXISTS(
        SELECT 1
        FROM fpl_team_players
        WHERE fpl_team_name = team_name AND 
            p_id = player_id AND
            u_id = user_id
    ) INTO is_in_team;
    RETURN is_in_team;
END !
DELIMITER ;

-- trigger to automatically 
DELIMITER !
CREATE TRIGGER tr_increase_team_value
AFTER INSERT ON fpl_team_players
FOR EACH ROW
BEGIN
    UPDATE fpl_team
    SET fpl_team_value = fpl_team_value + 
        (SELECT player_value FROM player WHERE player_id = NEW.player_id)
    WHERE fpl_team_name = NEW.fpl_team_name AND user_id = NEW.user_id;
END!

DELIMITER ;


DELIMITER !
CREATE TRIGGER tr_decrease_team_value
AFTER DELETE ON fpl_team_players
FOR EACH ROW
BEGIN
    UPDATE fpl_team
    SET fpl_team_value = fpl_team_value - 
        (SELECT player_value FROM player WHERE player_id = OLD.player_id)
    WHERE fpl_team_name = OLD.fpl_team_name AND user_id = OLD.user_id;
END!

DELIMITER ;