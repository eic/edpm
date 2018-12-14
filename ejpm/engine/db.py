"""
Packet state database stores the known information about packets

Like: name, installation path, installation date,
"""

import json
import os
import io
from ejpm.side_packages import provide_click_framework

# Try to import 'click' framework or to reference included version
provide_click_framework()  # Try to import 'click' framework or to reference included version
import click

# Make it work for Python 2+3 and with Unicode
try:
    # noinspection PyUnresolvedReferences
    to_unicode = unicode
except NameError:
    to_unicode = str


class PacketStateDatabase(object):
    """Class to persist installation knowledge """

    def __init__(self):
        self.file_path = ""

        self.data = {
            "file_version": 1,  # This data structure version, each time will increase by 1
            "installed": {},  # Data about known installations of packets
            "packets": {
                "root": {
                    "required": True,
                    "installs":
                    {'/home/romanov/jleic/test/root/bin/Linux__Ubuntu18.04-x86_64-gcc7/':
                        {
                            'is_ejpm_owned': False,
                            'is_selected': True
                        }
                    }
                },
                "clhep": {
                    "required": True,
                    "installs": {}
                },
                "genfit": {
                    "required": True,
                    "installs": {}
                },
                "rave": {
                    "required": True,
                    "installs": {}
                },
                "jana": {
                    "required": True,
                    "installs": {}
                },
                "ejana": {
                    "required": True,
                    "installs": {}
                },
            },
            "top_dir": "",
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

    @property
    def packet_names(self):
        return self.data['packets'].keys()

    def get_installs(self, packet_name):
        return self.data['packets'][packet_name]['installs'];

    def get_install(self, packet_name, path):
        """
        Returns installation information for a given packet and a given path

        :param packet_name: Name of the packet like root, jana, etc
        :type path: dict or None
        """
        if path in self.data['packets'][packet_name]['installs']:
            return path

    def update_install(self, packet_name, path, is_ejpm_owned, is_selected):
        installs = self.data['packets'][packet_name]['installs'];
        if path in installs.keys():
            install = installs[path]
        else:
            installs[path] = install = {}

        # deselect other installations if the new one is selected
        if is_selected:
            for prop in installs.values():
                prop["is_selected"] = False

        # set selected and ownership
        install["is_selected"] = is_selected
        install["is_ejpm_owned"] = is_ejpm_owned


    @property
    def missing(self):
        return [p for p in self.data['packets'].keys() if p not in self.data['installed'].keys()]

    @property
    def top_dir(self):
        return self.data["top_dir"]

    @top_dir.setter
    def top_dir(self, path):
        self.data["top_dir"] = path


# Create a database class and @pass_db decorator so our commands could use it
pass_db = click.make_pass_decorator(PacketStateDatabase, ensure=True)


