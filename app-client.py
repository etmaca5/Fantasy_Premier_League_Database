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
# MENU FUNCTIONS
# ----------------------------------------------------------------------


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

def show_options_menu():
    """
    Displays the main menu of the application.
    From here can go to the leaderboard, View stats,
    Change the players in one's team and quit the program
    """
    print('\nWhat would you like to do? ')
    print('  (c) - Quick Team Check')
    print('  (l) - View Leaderboard')
    print('  (s) - View Stats')
    print('  (p) - Change Players (%d players currently in the team)' % num_players)
    print('  (q) - Quit Program')
    print()
    ans = input('Enter an option: ').lower()
    if ans == 'q':
        quit_ui()
    elif ans == 'c':
        print("You now have %d player(s) and %d left in the bank" % (num_players, team_budget_remaining))
    elif ans == 'l':
        show_leaderboard()
    elif ans == 's':
        view_stats()
    elif ans == 'p':
        change_team_menu()
    else:
        print("Please enter a valid option")

def show_leaderboard():
    """
    Displays the leaderboard for the user and allows them to go back
    to the main menu if they need to want to
    """
    print("\n\n")
    sql_leaderboard = """
    SELECT fpl_team_name, points
    FROM fpl_team
    ORDER BY points DESC;
    """
    cursor = conn.cursor()
    try:
        cursor.execute(sql_leaderboard)
        rows = cursor.fetchall()
        print("LEADERBOARD:")
        for i in range(len(rows)):
            row = rows[i]
            print("Team name:", row[0], "points:", int(row[1]), "rank:", i + 1)
        print("\n\n")
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error with login occurred, please try again with another account')

def select_team_menu():
    """ 
    User can either create a team or select an existing team (under their user_id)
    If create team will be prompted to the change_players menu (where their 
    team will be empty)
    """
    print("Would you like to select a current team or create a new team:")
    print('  (s) - Select current team')
    print('  (n) - Create new team')
    ans = input('Enter an option: ').lower()
    if ans == 's':
        select_team()
    elif ans == 'n':
        create_team()
    else:
        print("Please enter a valid option")
        select_team_menu()
    # ensuring that the user has selected a team
    if fpl_team_name == "":
        # loops back if the team has no name
        select_team_menu()
    elif ans == 'n':
        # goes to change the menu if there are 0 players
        change_team_menu()

def change_team_menu():
    print("\nYou now have %d player(s) and %d left in the bank" % (num_players, team_budget_remaining))
    print("\nWould what you like to do:")
    print('  (v) - View your players')
    print('  (a) - Add players')
    print('  (r) - Remove players')
    print('  (s) - View Stats')
    print('  (e) - Exit to main menu')

    ans = input('Enter an option: ').lower()
    if ans == 'v':
        view_team_players()
        change_team_menu()
    elif ans == 'a':
        add_player()
        change_team_menu()
    elif ans == 'r':
        remove_player()
        change_team_menu()
    elif ans == 's':
        view_stats()
    elif ans == 'e':
        return
    else:
        print("Please enter a valid option")
        change_team_menu()
        



# ----------------------------------------------------------------------
# Command-Line Functionality
# ----------------------------------------------------------------------

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
    sql_password_info = 'CALL sp_add_user(%s, %s)'
    sql_add_user = 'INSERT INTO user (user_email, username) VALUES (%s, %s); '
    sql_get_user_id = 'SELECT user_id FROM user WHERE user_email = %s;'
    try:
        cursor.execute(sql_password_info, (username, password, ))
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


def select_team():
    global user_id
    cursor = conn.cursor()
    print("\nWhich team would you like to select:")
    sql_teams = """
    SELECT 
        ft.fpl_team_name, 
        ft.fpl_team_value, 
        COUNT(ftp.player_id) AS number_of_players
    FROM fpl_team ft
    LEFT JOIN fpl_team_players ftp ON ft.fpl_team_name = ftp.fpl_team_name
    WHERE ft.user_id = %s
    GROUP BY ft.fpl_team_name, ft.fpl_team_value;
    """
    try:
        cursor.execute(sql_teams, (user_id, ))
        rows = cursor.fetchall()
        if len(rows) == 0:
            print("Looks like you have no teams, please create a new team!\n")
            select_team_menu()
        else:
            print("Team names:")
            # holds all the teams with the num players and value
            teams = {}
            for row in rows:
                teams[row[0]] = (row[1], row[2])
                print('%s  -  with value: %d ' % (row[0] , row[1]))
            team_name = input("Please type in the name of a team: ")
            while team_name not in teams.keys():
                team_name = input("Please type in the name of a team from the above list: ")
            global fpl_team_name
            fpl_team_name = team_name
            global team_budget_remaining
            team_budget_remaining = STARTING_TEAM_VALUE - teams[team_name][0]
            global num_players
            num_players = teams[team_name][1]
            print("Succesfully selected team!\n")
        return True
    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred, please select a different team')
    return False

def create_team():
    global user_id
    cursor = conn.cursor()
    team_name = input("What would you like the name of your team to be: ")
    sql_add_team = 'CALL sp_add_team(%s, %s, %s);'
    try:
        cursor.execute(sql_add_team, (team_name, user_id, 0, ))
        conn.commit()
        global fpl_team_name
        fpl_team_name = team_name
        global team_budget_remaining
        team_budget_remaining = STARTING_TEAM_VALUE
    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred, please choose a different team name')


def view_team_players():
    global user_id
    # shows a user all their players in the current team they are in
    sql_get_team_query = """SELECT p.player_id,  p.player_name, p.team_name,
    p.position, p.player_value, p.total_points FROM fpl_team_players AS fpl JOIN player AS p ON 
    fpl.player_id = p.player_id WHERE fpl.user_id = %s AND fpl.fpl_team_name = %s; """
    cursor = conn.cursor()
    try:
        cursor.execute(sql_get_team_query, (user_id, fpl_team_name))
        rows = cursor.fetchall()
        print("\nFormat: Player_id, Name, Club, Position, Value, Total Points")
        for row in rows:
            print(row)
    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else: sys.stderr('Players cannot be shown at this time')
    return


def add_player():
    global team_budget_remaining
    global num_players
    global user_id
    if num_players >= 11:
        print("Cannot add a player, must remove one first")
        return 
    elif team_budget_remaining < LOWEST_PLAYER_COST:
        print("You cannot afford any other players. Sell other players if necessary")
        return
    cursor = conn.cursor()
    # this is the playerid
    player_to_add = 0
    player_value = STARTING_TEAM_VALUE + 1
    
    # need to add a valid player to the team
    while player_value > team_budget_remaining:
        player_to_add = int(input("\nWhat is the player_id of the player you'd like to add: "))
        sql_player_value = 'SELECT fn_get_player_value(%s);'
        try:
            cursor.execute(sql_player_value, (player_to_add, ))
            rows = cursor.fetchall()
            if(len(rows) == 0):
                print("Enter a valid player ID")
                continue
            player_value = rows[0][0]
            if player_value == None:
                print("Enter a valid player ID")
                continue
            print("player value: %d" % player_value)
        except mysql.connector.Error as err:
            if DEBUG:
                sys.stderr(err)
                sys.exit(1)
            else: sys.stderr('An error occurred, please choose a different player')
    sql_add_player = 'CALL sp_add_player(%s, %s, %s);'
    try:
        cursor.execute(sql_add_player, (fpl_team_name, player_to_add, user_id))
        conn.commit()
    except mysql.connector.Error as err:
        if DEBUG:
                sys.stderr(err)
                sys.exit(1)
        else: sys.stderr('An error occurred, please choose a different player')
    # remove the budget from the team
    team_budget_remaining -= player_value
    num_players += 1

def remove_player():
    global team_budget_remaining
    global num_players
    global user_id
    if num_players <= 0:
        print("Cannot remove a player, there are no players")
        return 
    cursor = conn.cursor()
    # this is the playerid
    player_to_remove = 0
    player_value = STARTING_TEAM_VALUE + 1
    
    # need to add a valid player to the team
    while True:
        player_to_remove = int(input("\nWhat is the player_id of the player you'd like to remove: "))
        sql_player_in_team = 'SELECT fn_check_player_team(%s, %s, %s);'
        sql_player_value = 'SELECT fn_get_player_value(%s);'
        try:
            cursor.execute(sql_player_in_team, (fpl_team_name, player_to_remove, user_id))
            in_team = cursor.fetchone()
            if not in_team or not in_team[0]:
                print("Enter a valid player ID which is in the team")
                continue
            cursor.execute(sql_player_value, (player_to_remove,))
            player_value_check = cursor.fetchone()
            if player_value_check is None:
                print("Couldn't get player, try again")
                continue
            player_value = player_value_check[0]
            print("Succesfully found player, value: " + str(player_value))
            break
        except mysql.connector.Error as err:
            if DEBUG:
                sys.stderr(err)
                sys.exit(1)
            else: sys.stderr('An error occurred, please choose a different player')
    sql_remove_player = 'CALL sp_remove_player(%s, %s, %s);'
    try:
        cursor.execute(sql_remove_player, (fpl_team_name, player_to_remove, user_id))
        conn.commit()
    except mysql.connector.Error as err:
        if DEBUG:
                sys.stderr(err)
                sys.exit(1)
        else: sys.stderr('An error occurred, please choose a different player')
    # add the budget
    team_budget_remaining += player_value
    num_players -= 1

def view_stats():
    """
    Displays the menu where the user can view the players' stats.
    Allows the user to go back to main menu or directly to the change
    players menu.
    """
    print('\nOptions:')
    print('  (p) - Change Players')
    print('  (e) - Exit to main menu')
    print('  (g) - Top Goalscorers')
    print('  (a) - Top Assisters')
    print('  (c) - Most Clean Sheets')
    print('  (m) - Most Minutes Played')
    print('  (b) - Most points')
    print('  (v) - Highest Value')
    print('  (i) - Misc')
    # TODO: add a bunch of options for different stats that can be looked at
    ans = input('Enter an option: ').lower()
    if ans == 'e':
        return
    elif ans == 'p':
        change_team_menu()
    elif ans in ['g', 'a', 'c', 'm', 'b', 'v']:
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
        elif ans == 'v':
            stat = "Value"
            sql = """
            SELECT player_id, player_name, position, player_value
            FROM player
            ORDER BY player_value DESC;       
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
            FROM player p
            JOIN matchweek m ON p.player_id = m.player_id
            GROUP BY p.player_id, p.player_name, p.position
            ORDER BY total_points DESC;
            """
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
            if(len(rows) == 0):
                print("No data available")
                return
            print('\n')
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
            print('\n')
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
    if ans in ['g', 'a', 'c', 'm', 'b', 'i']:
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
    select_team_menu()
    # once team selected keep coming back to the main menu
    while True:
        show_options_menu()


if __name__ == '__main__':
    # This conn is a global object that other functions can access.
    # You'll need to use cursor = conn.cursor() each time you are
    # about to execute a query with cursor.execute(<sqlquery>)
    conn = get_conn()
    main()
