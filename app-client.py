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
          database='shelterdb' # replace this with your database name
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
# CONSTANTS
# ----------------------------------------------------------------------
MAX_LOGIN_ATTEMPTS = 5

# ----------------------------------------------------------------------
# Functions for Command-Line Options/Query Execution
# ----------------------------------------------------------------------
def example_query():
    param1 = ''
    cursor = conn.cursor()
    # Remember to pass arguments as a tuple like so to prevent SQL
    # injection.
    sql = 'SELECT col1 FROM table WHERE col2 = \'%s\';' % (param1, )
    try:
        cursor.execute(sql)
        # row = cursor.fetchone()
        rows = cursor.fetchall()
        for row in rows:
            (col1val) = (row) # tuple unpacking!
            # do stuff with row data
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            # TODO: Please actually replace this :) 
            sys.stderr('An error occurred, give something useful for clients...')



# ----------------------------------------------------------------------
# Functions for Logging Users In
# ----------------------------------------------------------------------
# Note: There's a distinction between database users (admin and client)
# and application users (e.g. members registered to a store). You can
# choose how to implement these depending on whether you have app.py or
# app-client.py vs. app-admin.py (in which case you don't need to
# support any prompt functionality to conditionally login to the sql database)


# ----------------------------------------------------------------------
# Command-Line Functionality
# ----------------------------------------------------------------------
def show_options_menu():
    """
    Displays the main menu of the application.
    From here can go to the leaderboard, View stats,
    Change the players in one's team and quit the program
    """
    print('What would you like to do? ')
    print('  (l) - View Leaderboard')
    print('  (s) - View Stats')
    print('  (p) - Change Players')
    print('  (q) - Quit Program')
    print()
    ans = input('Enter an option: ').lower()
    if ans == 'q':
        quit_ui()
    elif ans == 'l':
        show_leaderboard()
    elif ans == 's':
        show_player_stats()
    elif ans == 'p':
        show_player_change_menu()
    elif ans == '':
        pass

def show_leaderboard():
    """
    Displays the leaderboard for the user and allows them to go back
    to the main menu if they need to want to
    """
    # TODO: print("ADD LEADERBOARD QUERY IN HERE")
    print('  (e) - Exit to main menu')
    print('  (p) - Change Players')
    ans = input('Enter an option: ').lower()
    if ans == 'e':
        show_options_menu()
    elif ans == '':
        pass

def show_player_change_menu():
    """
    Displays the menu where the user can change the players out from 
    their team. 
    Allows the user to go back to main menu once there are 11 players
    """
    
    print('  (s) - View stats')
    print('  (e) - Exit to main menu')
    ans = input('Enter an option: ').lower()
    # TODO: add condition: must be 11 players in the team in order to move
    # out of this menu
    if ans == 'e': 
        show_options_menu()
    if ans == 's': 
        show_player_stats()
    elif ans == '':
        pass

def show_player_stats():
    """
    Displays the menu where the user can view the players' stats.
    Allows the user to go back to main menu or directly to the change
    players menu.
    """
    print('  (p) - Change Players')
    print('  (e) - Exit to main menu')
    ans = input('Enter an option: ').lower()
    if ans == 'e':
        show_options_menu()
    elif ans == 'p':
        show_player_change_menu()
    elif ans == '':
        pass

def show_login_menu():
    """
    Displays the menu where the user can view the players' stats.
    Allows the user to go back to main menu or directly to the change
    players menu.
    """
    print('  (l) - Login')
    print('  (c) - Create Account')
    ans = input('Enter an option: ').lower()
    # ensuring that the user attempts to login or create an account
    while ans != 'l' or ans != 'c':
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
    login_true = input(
        'Would you like to login? (y) - yes, (n) - no, create account instead')
    if login_true == 'n':
        show_login_menu()
    user = input('Please enter your username: ')
    password  = input('Please enter your username: ')
    # TODO: add code which tests these in the database to see if correct
    return True

def create_account():
    user = input('Please enter your username: ')
    password  = input('Please enter your username: ')
    # TODO: add code which takes this username and password and adds it to db
    return True

def select_team_menu():
    """ 
    User can either create a team or select an existing team (under their user_id)
    If create team will be prompted to the change_players menu (where their 
    team will be emptu)
    """
    # TODO: team menu function, which will transition into the options menu or
    # the change players menu depending on the user's inpit
    # Function will display all of the users team and they can choose one of those
    # teams or they can move on



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
    show_options_menu()


if __name__ == '__main__':
    # This conn is a global object that other functions can access.
    # You'll need to use cursor = conn.cursor() each time you are
    # about to execute a query with cursor.execute(<sqlquery>)
    conn = get_conn()
    main()
