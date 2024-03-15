Our data comes from user vaastav on github. Link to the repository:
https://github.com/vaastav/Fantasy-Premier-League/tree/master

To setup the database open a SQL shell with the following commands:
SET GLOBAL local_infile = 1;
mysql --local-infile=1 -u root -p

Then run the following commands in the environment:
source setup.sql;
source load-data.sql;
source setup-routines.sql;
source setup-passwords.sql;
source grant-permissions.sql;

TODO: ADD on