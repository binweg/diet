#!/usr/bin/env python3
'''diet is a minimalistic calorie tracking program. It aims to offer the
capability of remembering the total calorie consumption per day.
'''

import argparse
import sys
import os
import collections
import pickle
import datetime

# determine path to store application data
# from http://stackoverflow.com/questions/1084697
appname = 'diet'
if sys.platform == 'darwin':
    from AppKit import NSSearchPathForDirectoriesInDomains
    appdata = os.path.join(NSSearchPathForDirectoriesInDomains(14, 1, True)[0],
        appname)
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

Food = collections.namedtuple('Food', ['calories', 'description'])

def get_food_db():
    '''reads the food database file from disk and returns the database
    '''
    with open(food_db_filename, 'rb') as food_db_file:
        return pickle.load(food_db_file)

def eat(args):
    '''eat is the method that executes either a lookup for the calories of a
    named piece of food from the food database or uses the calories provided
    by the user and adds them (multiplied by the number of portions) to the
    calorie database for the right day.

    args is an argparse Namespace object.
    '''
    # if we have to look the calories up...
    if args.food:
        food_db = get_food_db()
        # food_db contains dict with Food(namedtuple) values
        calories_base = food_db[args.food].calories
    # ...otherwise, we take the user-provided value
    else:
        calories_base = args.calories
    try:
        with open(calorie_db_filename, 'rb') as calorie_db_file:
            calorie_db = pickle.load(calorie_db_file)
    except FileNotFoundError:
        calorie_db = collections.Counter()
    day = datetime.date.today()
    # calories_base times portion size
    # product will be added to the daily total
    calories_to_add = calories_base * args.number
    calorie_db[day] += calories_to_add
    ensure_appdata_existence()
    with open(calorie_db_filename, 'wb') as calorie_db_file:
        pickle.dump(calorie_db, calorie_db_file)
    # print status _after_ file is written
    print('Added {:.0f} calories. Daily total: {:.0f}'.format(calories_to_add,
        calorie_db[day]))

def remember(args):
    '''remember is the method that stores the calories and the description in
    form of a Food object in the food database.

    args is an argparse Namespace object.
    '''
    food_data = Food(calories=args.calories, description=args.description)
    try:
        food_db = get_food_db()
    except FileNotFoundError:
        ensure_appdata_existence()
        food_db = dict()
    food_db[args.food] = food_data
    with open(food_db_filename, 'wb') as food_db_file:
        pickle.dump(food_db, food_db_file)

def lookup(args):
    '''lookup is the method that searches the food database for a food with the
    provided name and outputs their calories and descriptions.

    args is an argparse Namespace object.
    '''
    food_db = get_food_db()
    # the length of the longest match, used for formatting
    max_name_len = 0
    results = []
    if args.exact:
        def check_for_match(query):
            if args.search == query: return True
            return False
    else:
        search_lower = args.search.lower()
        def check_for_match(query):
            if search_lower in query.lower(): return True
            return False
    for food in food_db.keys():
        if check_for_match(food):
            results.append(food)
            if len(food) > max_name_len:
                max_name_len = len(food)
    headerformat = '{{0:<{m}}}  {{1:>5}}  {{2}}'.format(m=max_name_len)
    tableformat = '{{0:<{m}}}  {{1:>5.0f}}  {{2}}'.format(m=max_name_len)
    if results:
        if len(results) == 1:
            print('Found one match:\n')
        else:
            print('Found {} matches:\n'.format(len(results)))
        for food in sorted(results):
            food_data = food_db[food]
            print(tableformat.format(food,
                food_data.calories, food_data.description))
    else:
        print('Found no match.')

# This dictionary associates the methods with the commands from the argparse
# Namespace object
command_dispatcher = {'eat': eat, 'remember': remember, 'lookup': lookup}

parser = argparse.ArgumentParser(
    description='''diet is a minimalistic calorie tracking program.
        It aims to offer the capabilty of remembering the total calorie
        consumption per day.''')
subparsers = parser.add_subparsers(title='available commands',
    dest='command')

eat_parser = subparsers.add_parser('eat',
    description='''This command either looks up a given food in the database
        and adds it's calories to the daily total or adds the directly given
        amount of calories.''',
    usage='%(prog)s [-h] ([-c CAL] | FOOD)',
    help='add calories to the daily calorie count')

# either enter number of calories or food name:
choice_group = eat_parser.add_mutually_exclusive_group(required=True)
choice_group.add_argument('food', nargs='?', metavar='FOOD',
    help='the name of the food to add')
choice_group.add_argument('-c', '--calories', metavar='CAL', type=float,
    help='the number of calories per portion to add, instead of FOOD')

# needs to consider when calorie amount is given per 100g
# entering weight in grams might be preferred.
eat_parser.add_argument('-n', '--number', metavar='NUM', type=float, default=1,
    help='the number of times a calorie amount is added')

remember_parser = subparsers.add_parser('remember',
    description='''This command stores the given food with it's calories in the
    database to be later on accessed via the eat command.''',
    help='remember the calories of an item of food')
remember_parser.add_argument('food', metavar='FOOD',
    help='the name of the food to remember')
remember_parser.add_argument('calories', metavar='CAL', type=float,
    help='the number of calories of that item of food')
remember_parser.add_argument('description', metavar='DESC', nargs='?',
    help='an optional description', default='')

lookup_parser = subparsers.add_parser('lookup',
    description='''This command let's you look up a piece of food in the
    database and report it's calories and the associated description.''',
    help='look up piece of food in the database')
lookup_parser.add_argument('-e', '--exact', action='store_true',
    help='only look for one result that matches the search string exactly')
lookup_parser.add_argument('search', metavar='STRING',
    help='the string to look for')

if __name__ == '__main__':
    args = parser.parse_args()
    command_dispatcher[args.command](args)

