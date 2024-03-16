-- contains the queries for this project

-- this query finds all the players and their names 
-- TODO: change the actual values inside of the queries so that they work with the inputted data
SELECT 
    p.player_id, 
    p.player_name,
    p.position,
    p.player_value,
    p.total_points
FROM 
fpl_team_players AS fpl JOIN player AS p ON fpl.player_id = p.player_id
WHERE 
    fpl.user_id = 0 AND fpl.fpl_team_name = "e";

-- of course add basic queries for view stats


-- queries to add:
-- Answers:
-- 1. Selecting players who average over 0.05 points per minute, ordered by total points. 
-- This query would enable managers to see which players are consistently performing well.\
SELECT 
    player_id, 
    player_name, 
    team_name, 
    total_points, 
    player_value, 
    total_points / (IFNULL(minutes_played, 1)) AS points_per_minute
FROM 
    player
WHERE 
    (total_points / (IFNULL(minutes_played, 1))) > 0.05
ORDER BY 
    total_points DESC;



-- 3. Selecting all strikers, ordered by FPL “price” (their cost in the game). This 
-- query would allow managers to find players in a specific position that fit their budget.
SELECT 
    player_id, 
    player_name, 
    team_name, 
    player_value
FROM 
    player
WHERE 
    position = 'FWD'
ORDER BY 
    player_value;


-- 4. Finding the total number of managers who have a player. This query would allow 
-- administrators to see what players are the most popular, so they can update prices 
-- (ex. Increasing price for very popular players and decreasing price for unpopular players).
SELECT 
    p.player_id, 
    p.player_name, 
    COUNT(DISTINCT fpl.user_id) AS number_of_managers
FROM 
    player p
LEFT JOIN 
    fpl_team_players fpl ON p.player_id = fpl.player_id
GROUP BY 
    p.player_id, 
    p.player_name;
