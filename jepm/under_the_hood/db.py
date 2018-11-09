"""
Packet state database stores the known information about packets

Like: name, installation path, installation date,
"""

import json
import os
import io
from jepm.side_packages import provide_click_framework

# Try to import 'click' framework or to reference included version
provide_click_framework()   # Try to import 'click' framework or to reference included version
import click


# Make it work for Python 2+3 and with Unicode
try:
    # noinspection PyUnresolvedReferences
    to_unicode = unicode
except NameError:
    to_unicode = str


class PacketStateDatabase:
    """Class to persist installation knowledge """

    def __init__(self):
        self.file_path = ""

        self.data = {
            "file_version": 1,       # This data structure version, each time will increase by 1
            "installations": {}      # Data about known installations of packages
        }

        self.verbose = False

    def exists(self):
        """Returns True if db file exists

        self.file_path is used, it doesn't check is the file really exists or if it is a really our DB
        """
        return os.path.isfile(self.file_path)

    def save(self):
        """Saves self.data to a file self.file_path"""

        if not self.file_path:
            raise FileNotFoundError()

        # Write JSON file
        with io.open(self.file_path, 'w', encoding='utf8') as outfile:
            str_ = json.dumps(self.data,
                              indent=4, sort_keys=True,
                              separators=(',', ': '), ensure_ascii=False)
            outfile.write(to_unicode(str_))

    def load(self):
        """Loads self.data from a file with self.file_path"""

        # Read JSON file
        with open(self.file_path) as data_file:
            self.data = json.load(data_file)


# Create a database class and @pass_db decorator so our commands could use it
pass_db = click.make_pass_decorator(PacketStateDatabase, ensure=True)
