-- terminal command in order to be able to use local infile
-- SET GLOBAL local_infile = 1;
-- mysql --local-infile=1 -u root -p

DROP TRIGGER IF EXISTS tr_update_total_points;

-- load the players into the player tables
LOAD DATA LOCAL INFILE 'data/players.csv' INTO TABLE player
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;

-- trigger to update the points
DELIMITER !
CREATE TRIGGER tr_update_total_points
AFTER INSERT ON matchweek
FOR EACH ROW
BEGIN
    UPDATE player
    SET total_points = total_points + NEW.points
    WHERE player_id = NEW.player_id;
END!

DELIMITER ;


-- add each gameweek in
-- do this for each matchweek
-- gameweek 1
-- using these temporary tables and inserts allows data to be updated automatically
CREATE TEMPORARY TABLE staging_matchweek1 LIKE matchweek;

LOAD DATA LOCAL INFILE "data/gw1.csv" INTO TABLE staging_matchweek1
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;

INSERT INTO matchweek (player_id, matchweek, goals, assists, clean_sheets, minutes_played, points)
SELECT player_id, matchweek, goals, assists, clean_sheets, minutes_played, points
FROM staging_matchweek1;

DROP TABLE IF EXISTS staging_matchweek1;

-- gameweek 2
CREATE TEMPORARY TABLE staging_matchweek2 LIKE matchweek;

LOAD DATA LOCAL INFILE "data/gw2.csv" INTO TABLE staging_matchweek2
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;

INSERT INTO matchweek (player_id, matchweek, goals, assists, clean_sheets, minutes_played, points)
SELECT player_id, matchweek, goals, assists, clean_sheets, minutes_played, points
FROM staging_matchweek2;

DROP TABLE IF EXISTS staging_matchweek2;


