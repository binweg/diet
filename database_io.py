import sys
import os
import pickle

# determine path to store application data
# from http://stackoverflow.com/questions/1084697
appname = 'diet'
if sys.platform == 'darwin':
    from AppKit import NSSearchPathForDirectoriesInDomains
    appdata = os.path.join(
        NSSearchPathForDirectoriesInDomains(14, 1, True)[0],
        appname,
        )
elif sys.platform == 'win32':
    appdata = os.path.join(os.environ['APPDATA'], appname)
else:
    appdata = os.path.expanduser(os.path.join("~", "." + appname))

def ensure_appdata_existence():
    '''If the appdata directory doesn't exist at call time, create it.
    '''
    if not os.path.exists(appdata): os.makedirs(appdata)

# These are the paths for the files in which the calories per item of food
# and the calories per day are stored.
food_db_filename = os.path.join(appdata, 'food_db')
calorie_db_filename = os.path.join(appdata, 'calorie_db')
user_db_filename = os.path.join(appdata, 'user_db')

db_map = {
    'food': food_db_filename,
    'calorie': calorie_db_filename,
    'user': user_db_filename,
    }

def get_db(spec):
    '''reads the appropriate database file and returns the database

    spec is the type of database to return: food, calorie or user
    '''
    with open(db_map[spec], 'rb') as db_file:
        return pickle.load(db_file)

def put_db(spec, database):
    '''stores the database into the appropriate database file

    spec is the type of database: food, calorie or user
    '''
    with open(db_map[spec], 'wb') as db_file:
        pickle.dump(database, db_file)

