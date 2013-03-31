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
    help='add calories to the daily calorie count')
remember_parser = subparsers.add_parser('remember',
    help='remember the calories of an item of food')

if __name__ == '__main__':
    parser.parse_args()

