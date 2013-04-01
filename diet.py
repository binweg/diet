#!/usr/bin/env python3
'''diet is a minimalistic calorie tracking program. It aims to offer the
capability of remembering the total calorie consumption per day.
'''

import argparse
import sys
import os

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

parser = argparse.ArgumentParser(
    description='''diet is a minimalistic calorie tracking program.
        It aims to offer the capabilty of remembering the total calorie
        consumption per day.''')
subparsers = parser.add_subparsers(title='available commands')

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
choice_group.add_argument('-c', metavar='CAL',
    help='the number of calories per portion to add, instead of FOOD')

# needs to consider when calorie amount is given per 100g
# entering weight in grams might be preferred.
eat_parser.add_argument('-n', metavar='NUM',
    help='the number of times a calorie amount is added')

remember_parser = subparsers.add_parser('remember',
    description='''This command stores the given food with it's calories in the
    database to be later on accessed via the eat command.''',
    help='remember the calories of an item of food')
remember_parser.add_argument('food', metavar='FOOD',
    help='the name of the food to remember')
remember_parser.add_argument('calories', metavar='CAL',
    help='the number of calories of that item of food')
remember_parser.add_argument('description', metavar='DESC', nargs='?',
    help='an optional description')

if __name__ == '__main__':
    parser.parse_args()

