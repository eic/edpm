"""
Packet state database stores the known information about packets

Like: name, installation path, installation date,
"""

import json
import os
import io
from ejpm.engine.py23 import to_unicode

INSTALL_PATH = 'install_path'
IS_OWNED = 'is_owned'
IS_ACTIVE = 'is_active'


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
                    "installs": []
                },
                "clhep": {
                    "required": True,
                    "installs": []
                },
                "genfit": {
                    "required": True,
                    "installs": []
                },
                "rave": {
                    "required": True,
                    "installs": []
                },
                "jana": {
                    "required": True,
                    "installs": []
                },
                "ejana": {
                    "required": True,
                    "installs": []
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
            raise AssertionError()

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
        """Return packet names of known packets"""
        return self.data['packets'].keys()

    def get_installs(self, packet_name):
        return self.data['packets'][packet_name]['installs']

    def get_active_install(self, packet_name):
        installs = self.get_installs(packet_name)

        for install in installs:
            if install['is_active']:
                return install

        return None

    def get_active_installs(self):
        """Returns {name:{install_data}} of active installs"""
        return {name: self.get_active_install(name) for name in self.packet_names}

    def get_install(self, packet_name, path):
        """
        Returns installation information for a given packet and a given path

        :param packet_name: Name of the packet like root, jana, etc
        :type path: dict or None
        """
        if path in self.data['packets'][packet_name]['installs']:
            return path

    def update_install(self, packet_name, install_path, is_owned="nochange", is_active="nochange"):
        """

        :param packet_name: Name of the packet. Like root, genfit, rave, etc
        :param install_path: Path of the installation
        :param is_owned: Is owned and managed by EJPM
        :param is_active: Is active. Means is used to build other packets, etc
        :return:
        """

        installs = self.data['packets'][packet_name]['installs']
        install_path = os.path.normpath(install_path)

        # Search for existing installation with this installation path
        existing_install = None
        for install in installs:
            # We compare it just by == as all saved installs have gone through os.path.normpath
            if install[INSTALL_PATH] == to_unicode(install_path):
                existing_install = install
                break

        # If we didn't find an install, lets add a new one
        if existing_install is None:
            existing_install = {}
            installs.append(existing_install)
            existing_install[IS_ACTIVE] = True      # It is the first installation. Should be active
            existing_install[IS_OWNED] = False      # Nothing known about it, so guess we are not

        # set selected and ownership
        existing_install[INSTALL_PATH] = install_path
        if is_active != "nochange":
            # deselect other installations if the new one is selected
            if is_active:
                for install in installs:
                    install[IS_ACTIVE] = False
            existing_install[IS_ACTIVE] = is_active
        if is_owned != "nochange":
            existing_install[IS_OWNED] = is_owned

    #@property
    #def missing(self):
    #    return [p for p in self.data['packets'].keys() if self.data['installs']]

    @property
    def top_dir(self):
        return self.data["top_dir"]

    @top_dir.setter
    def top_dir(self, path):
        self.data["top_dir"] = path
