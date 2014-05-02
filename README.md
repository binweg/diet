# diet

*diet* is a minimalistic calorie tracking program. It aims to offer the capability of remembering the total calorie consumption per day. Contrary to popular existing calorie tracking applications, it

* doesn't use an prepopulated database of foods, which are of little use if the database language doesn't match the preferred language.
* allows fast definition of items without the need to first define the calorie amount per 100g if you happen to know how much calories a different portion has.
* has no long page load times that seem to be inappropriate considering the small size of information that you try to enter.

Finding the correct number of calories for some food is left to the user. If they can't be deferred from the packaging I recommend a lookup via [Wolfram|Alpha](http://www.wolframalpha.com) which provides a fast interface with little overhead. Wolfram|Alpha can be used to easily find a rough approximation for a [calorie goal](http://www.wolframalpha.com/input/?i=energy+expenditure).

## Usage

To add a piece of food to the database, use the `remember` command:

    ./diet.py remember cereal 683 'one medium bowl of cereal with milk'
    ./diet.py remember apple 91 

Once this piece of food is stored, it's calories can be added with the `eat` command:

    ./diet.py eat cereal
    Added 683 calories. Daily total: 683

If you don't want to permanently store some food, it's calories can be added directly with the `-c`/`--calories` flag:

    ./diet.py eat -c 105
    Added 105 calories. Daily total: 788

To set yourself a calorie goal, use the `set` command:

    ./diet.py set 2900

    ./diet.py eat apple
    Added 91 calories. Daily total: 879
    30% of targeted 2900 calories
     ------------------------------------------------------------------------------
    |========================                                                      |
     ------------------------------------------------------------------------------

