-- contains the queries for this project

-- this query finds all the players belonging to a certain fpl team
-- TODO: change the actual values inside of the queries so that they work with the inputted data
-- user_id and team_name are specific to user
SELECT 
    p.player_id, 
    p.player_name,
    p.position,
    p.player_value,
    p.total_points
FROM 
fpl_team_players AS fpl JOIN player AS p ON fpl.player_id = p.player_id
WHERE 
    fpl.user_id = 1 AND fpl.fpl_team_name = "e";

-- finds the number of players and the value of a given fpl team
SELECT 
    ft.fpl_team_name, 
    ft.fpl_team_value, 
    COUNT(ftp.player_id) AS number_of_players
FROM fpl_team ft
LEFT JOIN fpl_team_players ftp ON ft.fpl_team_name = ftp.fpl_team_name
WHERE ft.user_id = 1
GROUP BY ft.fpl_team_name, ft.fpl_team_value;



-- BASIC QUERIES FOR VIEW_STATS
-- finds the best goalscorers
SELECT p.player_id, p.player_name, p.position, SUM(m.goals) AS total_goals
FROM player p
JOIN matchweek m ON p.player_id = m.player_id
GROUP BY p.player_id, p.player_name, p.position
ORDER BY total_goals DESC;


-- finds the best assisters
SELECT p.player_id, p.player_name, p.position, SUM(m.assists) AS total_assists
FROM player p
JOIN matchweek m ON p.player_id = m.player_id
GROUP BY p.player_id, p.player_name, p.position
ORDER BY total_assists DESC;


-- finds the most clean sheets (only defenders and gks)
SELECT p.player_id, p.player_name, p.position, SUM(m.clean_sheets) AS total_clean_sheets
FROM player p
JOIN matchweek m ON p.player_id = m.player_id
WHERE p.position IN ('GK', 'DEF')
GROUP BY p.player_id, p.player_name, p.position
ORDER BY total_clean_sheets DESC;


-- finds the most minutes played
SELECT p.player_id, p.player_name, p.position, SUM(m.minutes_played) AS total_minutes_played
FROM player p
JOIN matchweek m ON p.player_id = m.player_id
GROUP BY p.player_id, p.player_name, p.position
ORDER BY total_minutes_played DESC;

-- finds the players with the most points
SELECT p.player_id, p.player_name, p.position, SUM(m.points) AS total_points
FROM player p
JOIN matchweek m ON p.player_id = m.player_id
GROUP BY p.player_id, p.player_name, p.position
ORDER BY total_points DESC;


-- MISCALLENEOUS QUERIES
-- 1. Selecting players who average over 0.05 points per minute, ordered by total points. 
-- This query would enable managers to see which players are consistently performing well.\
SELECT p.player_id, p.player_name, p.team_name, 
    SUM(m.points) AS total_points, p.player_value, 
    SUM(m.points) / NULLIF(SUM(m.minutes_played), 0) 
    AS points_per_minute
FROM player p JOIN matchweek m ON p.player_id = m.player_id
GROUP BY p.player_id, p.player_name, p.team_name, p.player_value
HAVING (SUM(m.points) / NULLIF(SUM(m.minutes_played), 0)) > 0.05
ORDER BY total_points DESC;


-- 2. Selecting all forwards, ordered by FPL “price” (their cost in the game). This 
-- query would allow managers to find players in a specific position that fit their budget.
SELECT player_id, player_name, team_name, player_value
FROM player
WHERE position = 'FWD'
ORDER BY player_value;

-- 3. Selecting all midfielders ordered by assists
-- query would allow managers to find players in a specific position that fit their budget.
SELECT p.player_id, p.player_name, SUM(m.assists) AS total_assists
FROM player p JOIN matchweek m ON p.player_id = m.player_id
WHERE p.position = 'MID'
GROUP BY p.player_id, p.player_name, p.position
ORDER BY total_assists;

-- 4. Finding the total number of managers who have a player. This query would allow 
-- administrators to see what players are the most popular, so they can update prices 
-- (ex. Increasing price for very popular players and decreasing price for unpopular players).
SELECT p.player_id, p.player_name, 
    COUNT(DISTINCT fpl.user_id) AS number_of_managers
FROM player p
LEFT JOIN fpl_team_players fpl ON p.player_id = fpl.player_id
GROUP BY p.player_id, p.player_name
ORDER BY number_of_managers;

-- LEADERBOARD STANDINGS
SELECT fpl_team_name, points
FROM fpl_team
ORDER BY points DESC;
