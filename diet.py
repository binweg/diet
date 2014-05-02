#!/usr/bin/env python3
"""
diet is a minimalistic calorie tracking program. It aims to offer the
capability of remembering the total calorie consumption per day.
"""

import argparse
import datetime
import re
import sys

from database_io import DB, to_key


def search_food(regex):
    """
    Search food database for keys that contain a certain regular expression.
    """
    pattern = re.compile(regex, re.IGNORECASE)
    results = [food for food in db.data['food'] if re.search(pattern, food)]
    return results


def print_bar(total, target, display_area=80):
    """
    Print a progress bar that shows how many calories have been eaten.
    If the total is larger than the target, the border will be drawn shorter
    to maintain all proportions and the overall width of the bar.
    """
    if total < target:
        bar_width = display_area
        fill_width = round(display_area * total / target)
    else:
        bar_width = round(target / total * display_area)
        fill_width = display_area
    print(' ' + '-' * (bar_width - 2) + ' ')
    bar = '=' * fill_width + ' ' * (display_area - fill_width)
    print('|' + bar[:bar_width - 2] + '|' + bar[bar_width:])
    print(' ' + '-' * (bar_width - 2) + ' ')


def print_status(total, date_offset, day, added=None):
    day_format = {
        0: 'today',
        1: 'yesterday',
        }
    if added is None:
        format_string = 'Daily total for {day}: {total}'
    else:
        format_string = ('Added {added:.0f} calories for {day}. '
                         + 'Daily total: {total:.0f}')
    message = format_string.format(
        added=added,
        day=day_format.get(date_offset, day.strftime('%A, %Y-%m-%d')),
        total=total,
        )
    print(message)
    if 'target' in db.data['user']:
        target = db.data['user']['target']
        message = '{:.0%} of targeted {:.0f} calories'.format(
            total / target,
            target,
            )
        print(message)
        print_bar(total, target)


def status(args):
    """
    Print the user's calories.
    """
    day = datetime.date.today() - datetime.timedelta(days=args.yesterday)
    day_key = to_key(day)
    total = db.data['calories'].get(day_key, 0)
    print_status(
        total=total,
        date_offset=args.yesterday,
        day=day,
        )


def eat(args):
    """
    eat is the method that executes either a lookup for the calories of a
    named piece of food from the food database or uses the calories provided
    by the user and adds them (multiplied by the number of portions) to the
    calorie database for the right day.

    args is an argparse Namespace object.
    """
    # if we have to look the calories up...
    if args.food:
        # food_db contains dict with Food(namedtuple) values
        try:
            calories_base = db.data['food'][args.food]['cal']
        except KeyError:
            results = search_food(args.food)
            if len(results) == 1:
                message = (
                    "No match for '{}', but found '{}'. Using this instead."
                    .format(args.food, results[0]))
                print(message)
                calories_base = db.data['food'][results[0]]['cal']
            else:
                print("Could not find '{}' in the food database."
                      .format(args.food))
                return
    # ...otherwise, we take the user-provided value
    else:
        calories_base = args.calories

    day = datetime.date.today() - datetime.timedelta(days=args.yesterday)
    day_key = to_key(day)
    # calories_base times portion size
    # product will be added to the daily total
    calories_to_add = calories_base * args.number
    try:
        db.data['calories'][day_key] += calories_to_add
    except KeyError:
        db.data['calories'][day_key] = calories_to_add
    db.write_data()
    # print status _after_ file is written
    print_status(
        total=db.data['calories'][day_key],
        date_offset=args.yesterday,
        day=day,
        added=calories_to_add,
        )


def remember(args):
    """
    remember is the method that stores the calories and the description in
    form of a dict in the food database.

    args is an argparse Namespace object.
    """
    food_data = {
        'cal': args.calories,
        'desc': args.description,
        }
    db.data['food'][args.food] = food_data
    db.write_data()


def forget(args):
    """
    forget removes a given item from the food database.
    """
    if args.food in db.data['food']:
        del db.data['food'][args.food]
        db.write_data()


def lookup(args):
    """
    lookup is the method that searches the food database for a food with the
    provided name and outputs their calories and descriptions.

    args is an argparse Namespace object.
    """
    results = []
    if args.exact:
        if args.food in db.data['food']:
            results = [args.food]
    else:
        results = search_food(args.food)
    if results:
        max_name_len = max(map(len, results))
        header_format = '{{0:<{m}}}  {{1:>5}}  {{2}}'.format(m=max_name_len)
        table_format = ('{{0:<{m}}}  {{1[cal]:>5.0f}}  {{1[desc]}}'
                        .format(m=max_name_len))

        if len(results) == 1:
            print('Found one match:\n')
        else:
            print('Found {} matches:\n'.format(len(results)))
        header = header_format.format('name', 'cal', 'description')
        print(header)
        for food in sorted(results):
            food_data = db.data['food'][food]
            table_line = table_format.format(food, food_data)
            print(table_line)
    else:
        print('Found no match.')


def user_set(args):
    """
    set values of personal variables and store into user database.
    """
    if not args.target is None:
        db.data['user']['target'] = args.target
        # don't let target produce zero division
        if args.target == 0:
            del db.data['user']['target']
        db.write_data()

# This dictionary associates the methods with the commands from the argparse
# Namespace object
command_dispatcher = {
    'eat': eat,
    'remember': remember,
    'forget': forget,
    'lookup': lookup,
    'set': user_set,
    'status': status,
    }

parser = argparse.ArgumentParser(
    description='''diet is a minimalistic calorie tracking program.
        It aims to offer the capability of remembering the total calorie
        consumption per day.''',
    )
subparsers = parser.add_subparsers(
    title='available commands',
    dest='command',
    )

eat_parser = subparsers.add_parser(
    'eat',
    description='''This command either looks up a given food in the database
        and adds it's calories to the daily total or adds the directly given
        amount of calories.''',
    usage='%(prog)s [-h] [-y] [-n NUM] {[-c CAL] | FOOD}',
    help='add calories to the daily calorie count',
    )

# either enter number of calories or food name:
choice_group = eat_parser.add_mutually_exclusive_group(required=True)
choice_group.add_argument(
    'food',
    nargs='?',
    metavar='FOOD',
    help='the name of the food to add',
    )
choice_group.add_argument(
    '-c', '--calories',
    metavar='CAL',
    type=float,
    help='the number of calories per portion to add, instead of FOOD',
    )

# needs to consider when calorie amount is given per 100g
# entering weight in grams might be preferred.
eat_parser.add_argument(
    '-n', '--number',
    metavar='NUM',
    type=float,
    default=1,
    help='the number of times a calorie amount is added',
    )
eat_parser.add_argument(
    '-y', '--yesterday',
    action='count',
    default=0,
    help='''add the calories to yesterday's instead of today's count.
        Can be repeated to address earlier days.''',
    )

remember_parser = subparsers.add_parser(
    'remember',
    description='''This command stores the given food with it's calories in the
        database to be later on accessed via the eat command.''',
    help='remember the calories of an item of food',
    )
remember_parser.add_argument(
    'food',
    metavar='FOOD',
    help='the name of the food to remember',
    )
remember_parser.add_argument(
    'calories',
    metavar='CAL',
    type=float,
    help='the number of calories of that item of food',
    )
remember_parser.add_argument(
    'description',
    metavar='DESC',
    nargs='?',
    help='an optional description',
    default='',
    )

status_parser = subparsers.add_parser(
    'status',
    description='''This command shows you how many calories you've consumed
        already.''',
    help="show how many calories you've consumed",
    )
status_parser.add_argument(
    '-y', '--yesterday',
    action='count',
    default=0,
    help='''show calories for yesterday instead of today.
        Can be repeated to address earlier days.''',
    )

forget_parser = subparsers.add_parser(
    'forget',
    description='''This command lets you remove a piece of food from the food
        database.''',
    help='remove food from database',
    )
forget_parser.add_argument(
    'food',
    metavar='FOOD',
    help='the name of the food to remove',
    )

lookup_parser = subparsers.add_parser(
    'lookup',
    description='''This command let's you look up a piece of food in the
        database and report it's calories and the associated description.''',
    help='look up piece of food in the database',
    )
lookup_parser.add_argument(
    '-e', '--exact',
    action='store_true',
    help='only look for one result that matches the search string exactly',
    )
lookup_parser.add_argument(
    'food',
    metavar='STRING',
    help='the string to look for',
    )

set_parser = subparsers.add_parser(
    'set',
    description='''This command let's you store values for personal parameters.
        They will be considered in the status message to be printed after
        invocation of the `eat` command.''',
    help='set personal parameters of which later status messages depend upon',
    )
set_parser.add_argument(
    'target',
    metavar='TARGET',
    type=float,
    help='the targeted total amount of calories per day',
    )

if __name__ == '__main__':
    # Print help if program is called without arguments.
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    arguments = parser.parse_args()
    db = DB(directory='default', file='db.json')
    command_dispatcher[arguments.command](arguments)
