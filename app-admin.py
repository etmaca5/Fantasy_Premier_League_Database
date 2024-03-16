"""
Student name(s): Etienne Casanova, Jack Myles
Student email(s): ecasanov@caltech.edu, jmyles@caltech.edu
Program Overview:
This program is a database with a collection of Fantasy Premier League 
statistics from the current English Premier League season (soccer).
These include stats on players and teams, such as goals, assists, wins, 
losses, etc. The primary application will be the ability to view various 
leaderboards of statistics, with the purpose of allowing Fantasy Premier 
League managers to determine who they should select for their team. Managers 
will be able to create a team of 11 players given a budget and track their 
team's overall performance. 
"""
# TODO: Make sure you have these installed with pip3 if needed
import sys  # to print error messages to sys.stderr
import csv
import mysql.connector
# To get error codes from the connector, useful for user-friendly
# error-handling
import mysql.connector.errorcode as errorcode

# Debugging flag to print errors when debugging that shouldn't be visible
# to an actual client. ***Set to False when done testing.***
DEBUG = True


# ----------------------------------------------------------------------
# SQL Utility Functions
# ----------------------------------------------------------------------
def get_conn():
    """"
    Returns a connected MySQL connector instance, if connection is successful.
    If unsuccessful, exits.
    """
    try:
        conn = mysql.connector.connect(
          host='localhost',
          user='appadmin',
          # Find port in MAMP or MySQL Workbench GUI or with
          # SHOW VARIABLES WHERE variable_name LIKE 'port';
          port='3306',  # this may change!
          password='adminpw',
          database='fpldb'
        )
        print('Successfully connected.')
        return conn
    except mysql.connector.Error as err:
        # Remember that this is specific to _database_ users, not
        # application users. So is probably irrelevant to a client in your
        # simulated program. Their user information would be in a users table
        # specific to your database; hence the DEBUG use.
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR and DEBUG:
            sys.stderr('Incorrect username or password when connecting to DB.')
        elif err.errno == errorcode.ER_BAD_DB_ERROR and DEBUG:
            sys.stderr('Database does not exist.')
        elif DEBUG:
            sys.stderr(err)
        else:
            # A fine catchall client-facing message.
            sys.stderr('An error occurred, please contact the administrator.')
        sys.exit(1)

# ----------------------------------------------------------------------
# CONSTANTS and global vars
# ----------------------------------------------------------------------
MAX_LOGIN_ATTEMPTS = 5
STARTING_TEAM_VALUE = 800
LOWEST_PLAYER_COST = 40
user_id = -1
fpl_team_name = ""
team_budget_remaining = 0
num_players = 0

# ----------------------------------------------------------------------
# Functions for Logging Users In
# ----------------------------------------------------------------------
# Note: There's a distinction between database users (admin and client)
# and application users (e.g. members registered to a store). You can
# choose how to implement these depending on whether you have app.py or
# app-client.py vs. app-admin.py (in which case you don't need to
# support any prompt functionality to conditionally login to the sql database)

def show_login_menu():
    """
    Displays the menu where the user can login or create an account.
    """
    print('  (l) - Login')
    print('  (c) - Create Account')
    ans = input('Enter an option: ').lower()
    # ensuring that the user attempts to login or create an account
    while ans != 'l' and ans != 'c':
        print('  (l) - Login')
        print('  (c) - Create Account')
        ans = input('Either login or create an account: ').lower()
    if ans == 'l':
        # user decides to login
        num_login_attempts = 0
        correct_login = login_attempt()
        while correct_login == False:
            correct_login = login_attempt()
            num_login_attempts += 1
            if num_login_attempts >= 5:
                print("Too many attempts have been failed!")
                quit_ui()
    elif ans == 'c':
        # user decides to create an account
        create_account()

def login_attempt():
    """
    Called when user tries to login, allows them to go back to the main page
    and create a new account at any point.
    Returns False if the login attempt was incorrect and true if it was correct
    """
    global user_id
    cursor = conn.cursor()
    print('\nWould you like to login?')
    print('  (y) - yes')
    print('  (n) - no, create account instead')
    login_true = input('Enter an option: ').lower()
    if login_true == 'n':
        show_login_menu()
    username = input('\nPlease enter your username: ')
    password  = input('Please enter your password: ')
    sql_login = "SELECT authenticate(%s, %s);"
    sql_get_user_id = 'SELECT user_id FROM user WHERE username = %s;'
    try:
        cursor.execute(sql_login, (username, password, ))
        rows_authen = cursor.fetchall()
        if rows_authen[0][0] == 1:
            print("Authenticated!")
            cursor.execute(sql_get_user_id, (username, ))
            rows = cursor.fetchall()
            if(len(rows) == 0):
                print("There is an issue with the program")
                quit
            user_id = (rows[-1])[0]
            print("Successfully logged in!\n")
            return True
        else:
            print("Incorrect username or password\n")
            return False

    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error with login occurred, please try again with another account')
    return False

def create_account():
    global user_id
    # creates an account for the user
    cursor = conn.cursor()
    email = input('Please enter your email: ')
    username = input('Please enter your username: ')
    password  = input('Please enter your password: ')
    sql_password_info = 'CALL sp_add_user(%s, %s, %s)'
    sql_add_user = 'INSERT INTO user (user_email, username) VALUES (%s, %s); '
    sql_get_user_id = 'SELECT user_id FROM user WHERE user_email = %s;'
    try:
        cursor.execute(sql_password_info, (username, password, 0, ))
        conn.commit()
        cursor.execute(sql_add_user, (email, username, ))
        cursor.execute(sql_get_user_id, (email, ))
        rows = cursor.fetchall()
        # sets the global variable user_id
        user_id = (rows[-1])[0]
        print("Succesfully created new account!\n")
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred, please use a different username and password')
    return True


# ----------------------------------------------------------------------
# Command-Line Functionality
# ----------------------------------------------------------------------
def show_options_menu():
    """
    Displays the main menu of the application.
    From here can view stats, add matchweek data, add players,
    update a player's value, and quit the program
    """
    print('\nWhat would you like to do? ')
    print('  (s) - View Stats')
    print('  (m) - Add Matchweek Data')
    print('  (v) - Update Player Value')
    print('  (p) - Add Player')
    print('  (q) - Quit Program')
    print()
    ans = input('Enter an option: ').lower()
    if ans == 'q':
        quit_ui()
    elif ans == 'm':
        add_matchweek()
    elif ans == 'v':
        update_player_value()
    elif ans == 's':
        view_stats()
    elif ans == 'p':
        add_player()
    else:
        print("Please enter a valid option")

def add_matchweek():
    """
    Allows an admin to add the data for a matchweek in the form of a CSV file
    """
    cursor = conn.cursor()
    sql_insert = 'INSERT INTO matchweek (player_id, matchweek, goals, \
        assists, clean_sheets, minutes_played, points) \
        VALUES (%s, %s, %s, %s, %s, %s, %s); '

    while True:
        f = input("Enter the filename for the matchweek data: ")
        if not f.endswith('.csv'):
            print("Please input a CSV file.")
            continue
        try:
            with open(f, 'r') as data:
                reader = csv.reader(data, delimiter=',')
                header = next(reader, None)
                if header != ['player_id', 'matchweek', 'goals' , 'assists',
                              'clean_sheets', 'minutes_played', 'points']:
                    print("CSV file has incorrect format.")
                    continue
                for row in reader:
                    try:
                        cursor.execute(sql_insert, (row[0], row[1], row[2],
                                                    row[3], row[4], row[5],
                                                    row[6], ))
                        conn.commit()
                    except mysql.connector.Error as err:
                        if DEBUG:
                            sys.stderr(err)
                            sys.exit(1)
                        else: sys.stderr('An error occurred')
                break
        except FileNotFoundError:
            print("File not found. Please input a valid file.")

def add_player():
    cursor = conn.cursor()
    player_id = input("Enter the new player's ID: ")
    player_name = input("Enter the new player's name: ")
    team_name = input("Enter the new player's team: ")
    position = input("Enter the new player's position (GK, DEF, MID, FWD): ")
    player_value = input("Enter the new player's value: ")
    total_points = 0
    sql_insert = 'INSERT INTO player (player_id, player_name, team_name, \
        position, player_value, total_points) \
        VALUES (%s, %s, %s, %s, %s, %s); '
    try:
        cursor.execute(sql_insert, (player_id, player_name, team_name,
                                    position, player_value, total_points, ))
        conn.commit()
    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else: sys.stderr('An error occurred')

def update_player_value():
    """
    Allows an admin to update a player's value.
    """
    player_id = input('Enter the player_id to be updated: ')
    # TODO: Add code to input data into database

def view_stats():
    """
    Displays the menu where the user can view the players' stats.
    Allows the user to go back to main menu or directly to the change
    players menu.
    """
    print('\nOptions:')
    print('  (e) - Exit to main menu')
    print('  (g) - Top Goalscorers')
    print('  (a) - Top Assisters')
    print('  (c) - Most Clean Sheets')
    print('  (m) - Most Minutes Played')
    print('  (b) - Most points')
    print('  (i) - Misc')
    # TODO: add a bunch of options for different stats that can be looked at
    ans = input('Enter an option: ').lower()
    if ans == 'e':
        return
    elif ans in ['g', 'a', 'c', 'm', 'b']:
        num_best = int(input("How long would you like the list of top players to be: "))
        sql = ''
        stat = ""
        if ans == 'g':
            stat = "Total Goals"
            sql = """
            SELECT p.player_id, p.player_name, p.position, SUM(m.goals) AS total_goals
            FROM player p
            JOIN matchweek m ON p.player_id = m.player_id
            GROUP BY p.player_id, p.player_name, p.position
            ORDER BY total_goals DESC;
            """
        elif ans == 'a':
            stat = "Total Assists"
            sql = """
            SELECT p.player_id, p.player_name, p.position, SUM(m.assists) AS total_assists
            FROM player p
            JOIN matchweek m ON p.player_id = m.player_id
            GROUP BY p.player_id, p.player_name, p.position
            ORDER BY total_assists DESC;       
            """
        elif ans == 'c':
            stat = "Total Clean Sheets"
            sql = """
            SELECT p.player_id, p.player_name, p.position, SUM(m.clean_sheets) AS total_clean_sheets
            FROM player p
            JOIN matchweek m ON p.player_id = m.player_id
            WHERE p.position IN ('GK', 'DEF')
            GROUP BY p.player_id, p.player_name, p.position
            ORDER BY total_clean_sheets DESC;
            """
        elif ans == 'm':
            stat = "Total Minutes Played"
            sql = """
            SELECT p.player_id, p.player_name, p.position, SUM(m.minutes_played) AS total_minutes_played
            FROM player p
            JOIN matchweek m ON p.player_id = m.player_id
            GROUP BY p.player_id, p.player_name, p.position
            ORDER BY total_minutes_played DESC;
            """
        elif ans == 'b':
            stat = "Total Points"
            sql = """
            SELECT p.player_id, p.player_name, p.position, SUM(m.points) AS total_points
            FROM player player_id
            GROUP BY p.player_id, p.player_
            JOIN matchweek m ON p.player_id = m.pname, p.position
            ORDER BY total_points DESC;
            """
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
            if(len(rows) == 0):
                print("No data available")
                return
            print("Format: Player_id, Name, Position, %s " % stat)
            for i in range(num_best):
                row = rows[i]
                print(row[0], row[1], row[2], int(row[3]),  stat)
        except mysql.connector.Error as err:
            if DEBUG:
                sys.stderr(err)
                sys.exit(1)
            else: sys.stderr('An error occurred, please choose different statistics')
    elif ans == 'i':
        print("Choose one of the following statistics: ")
        print("  (a) - Players who average over 0.05 points per minute")
        print("  (b) - All Forwards ordered by price")
        print("  (c) - All Midfielders ordered by assists")
        print("  (d) - Top 20 most selected players (by managers)")
        adv_ans = input("Select a statistic from above: ")
        sql = ""
        stat = ""
        format = ""
        if adv_ans == 'a':
            stat = "Players who average over 0.05 points per minute"
            format = "Player ID, Name, Club, Total Points, Value, Points Per Minute"
            sql = """
            SELECT p.player_id, p.player_name, p.team_name, 
                SUM(m.points) AS total_points, p.player_value, 
                SUM(m.points) / NULLIF(SUM(m.minutes_played), 0) 
                AS points_per_minute
            FROM player p JOIN matchweek m ON p.player_id = m.player_id
            GROUP BY p.player_id, p.player_name, p.team_name, p.player_value
            HAVING (SUM(m.points) / NULLIF(SUM(m.minutes_played), 0)) > 0.05
            ORDER BY total_points DESC;
            """
        elif adv_ans == 'b':
            stat = "All forwards ordered by price"
            format = "Player ID, Name, Club, Value"
            sql = """
            SELECT player_id, player_name, team_name, player_value
            FROM player
            WHERE position = 'FWD'
            ORDER BY player_value;
            """
        elif adv_ans == 'c':
            stat = "All Midfielders ordered by assists"
            format = "Player ID, Name, Total Assists"
            sql = """
            SELECT p.player_id, p.player_name, SUM(m.assists) AS total_assists
            FROM player p JOIN matchweek m ON p.player_id = m.player_id
            WHERE p.position = 'MID'
            GROUP BY p.player_id, p.player_name, p.position
            ORDER BY total_assists;
            """
        elif adv_ans == 'd':
            stat = "Top 20 most selected players (by managers)"
            format = "Player ID, Name, Number of Times Selected"
            sql = """
            SELECT p.player_id, p.player_name, 
                COUNT(DISTINCT fpl.user_id) AS number_of_managers
            FROM player p
            LEFT JOIN fpl_team_players fpl ON p.player_id = fpl.player_id
            GROUP BY p.player_id, p.player_name
            ORDER BY number_of_managers;
            """
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
            if(len(rows) == 0):
                print("No data available")
                return
            print(stat)
            print(format)
            if adv_ans == 'a':
                for row in rows:
                    print(row[:3], int(row[3]), "Total Points", int(row[4]), "Value", float(row[5]), "PPM")
            elif adv_ans == 'd':
                # print top 20 for misc 'd'
                for i in range(20):
                    row = rows[i]
                    print(row[0], row[1], int(row[2]))
            else:
                for row in rows:
                    print(row[:-1], int(row[-1]))            
        except mysql.connector.Error as err:
            if DEBUG:
                sys.stderr(err)
                sys.exit(1)
            else: sys.stderr('An error occurred, please choose a different statistic')
    else:
        view_stats()


def quit_ui():
    """
    Quits the program, printing a good bye message to the user.
    """
    print('Good bye!')
    exit()


def main():
    """
    Main function for starting things up.
    """
    show_login_menu()
    # once login menu passes go to select team menu, which then will transition
    # to the main options menu
    while True:
        show_options_menu()


if __name__ == '__main__':
    # This conn is a global object that other functions can access.
    # You'll need to use cursor = conn.cursor() each time you are
    # about to execute a query with cursor.execute(<sqlquery>)
    conn = get_conn()
    main()
