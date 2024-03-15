-- Create users, one admin and one client
CREATE USER 'appadmin'@'localhost' IDENTIFIED BY 'adminpw';
CREATE USER 'appclient'@'localhost' IDENTIFIED BY 'clientpw';
-- Grant privileges to each user
GRANT ALL PRIVILEGES ON fpldb.* TO 'appadmin'@'localhost';
GRANT SELECT ON fpldb.* TO 'appclient'@'localhost';
FLUSH PRIVILEGES;
