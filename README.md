Project by: Etienne Casanova and Jack Myles

Fantasy Premier League Database and Command line interface.
Data comes from user vaastav on github. Link to the repository:
https://github.com/vaastav/Fantasy-Premier-League/tree/master

To setup the database open a SQL shell with the following commands:
SET GLOBAL local_infile = 1;
mysql --local-infile=1 -u root -p

Then run the following commands in the SQL environment:

For first time run:
CREATE DATABASE fpldb;
USE fpldb;

Then always run:
source setup.sql;
source load-data.sql;
source setup-routines.sql;
source setup-passwords.sql;
source grant-permissions.sql;
source queries.sql;
quit;

Then run:
python3 app-client.py

Note: for a continued fantasy premier league experience additional gameweek data must be imported (same format as gw1.csv)