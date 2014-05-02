import json
import sys
import os


def get_suggested_dir():
    """
    Determine the default directory to store application data.

    from http://stackoverflow.com/questions/1084697
    """
    app_name = 'diet'
    if sys.platform == 'darwin':
        from AppKit import NSSearchPathForDirectoriesInDomains
        appdata_dir = os.path.join(
            NSSearchPathForDirectoriesInDomains(14, 1, True)[0],
            app_name,
        )
    elif sys.platform == 'win32':
        appdata_dir = os.path.join(os.environ['APPDATA'], app_name)
    else:
        appdata_dir = os.path.expanduser(os.path.join("~", "." + app_name))
    return appdata_dir


class DB:
    """
    Database class with json read/write ability

    No insert/query/etc. methods, only access to self.data
    """

    def __init__(self, directory='default', file='db.json'):
        """
        Create a database instance that reads a json file from disk
        and provides access the underlying dictionary.
        """
        self.data = {
            'food': {},
            'calories': {},
            'user': {},
            }

        if directory == 'default':
            self._directory = get_suggested_dir()
            self._path = os.path.join(get_suggested_dir(), file)
        else:
            self._path = os.path.join(directory, file)

        self._read_data()

    def _read_data(self):
        """
        Read the data from the json file and cache it locally.
        """
        try:
            with open(self._path, 'r') as json_file:
                self.data = json.load(json_file)
        except FileNotFoundError:
            pass

    def write_data(self):
        """
        Write the cached data into the json file.
        """
        if not os.path.exists(self._directory):
            os.makedirs(self._directory)

        with open(self._path, 'w') as json_file:
            json.dump(self.data, json_file, sort_keys=True, indent=4)


def to_key(date):
    """
    Turn a datetime object into the string representation
    so that it can be stored as a json key.
    """
    day_format = '%Y-%m-%d'
    return date.strftime(day_format)
