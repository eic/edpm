"""
Packet state database stores the known information about packets

Like: name, installation path, installation date,
"""

import json
import os
import io
from ejpm.engine.py23 import to_unicode

INSTALL_PATH = 'install_path'
SOURCE_PATH = 'source_path'
BUILD_PATH = 'build_path'
IS_OWNED = 'is_owned'
IS_ACTIVE = 'is_active'


class PacketStateDatabase(object):
    """Class to persist installation knowledge """

    def __init__(self):
        self.file_path = ""

        # This field is set during runtime by packet manager knoweledge
        self.known_packet_names = []

        self.data = {
            "file_version": 3,  # This data structure version, each time will increase by 1
            "packets": {},      # create_packet_minimal_data() is used to create data inside this field
            "top_dir": "",      # The directory where everything is installed
            "packet_stack_name": "default"
        }

        self.verbose = False
        self.is_loaded = False

    @staticmethod
    def create_packet_minimal_data():
        return {"installs": []}
    
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

        self.is_loaded = True

    def load(self):
        """Loads self.data from a file with self.file_path"""

        # Read JSON file
        with open(self.file_path) as data_file:
            self.data = json.load(data_file)
            self._update_schema()

        self.is_loaded = True

    @property
    def packet_names(self):
        """Return packet names of known packets"""
        return self.data['packets'].keys()

    def get_installs(self, packet_name):
        """Get all installation information (like location) for packet with this name """

        # If we have no record in the packet installations, but we know the name is OK
        if packet_name not in self.data['packets'].keys() and packet_name in self.known_packet_names:
            self.data['packets'][packet_name] = {"installs": []}

        # Return whatever we can (or it will raise KeyException)
        return self.data['packets'][packet_name]['installs']

    def get_active_install(self, packet_name):
        """Get installation marked as 'is_active' from all installations of packet with name 'packet_name'"""

        installs = self.get_installs(packet_name)

        for install in installs:
            assert isinstance(install, dict)
            if install[IS_ACTIVE]:
                return install

        return None

    def get_active_installs(self):
        """Returns {name:{install_data}} of active installs"""
        return {name: self.get_active_install(name) for name in self.packet_names}

    def get_install(self, packet_name, install_path):
        """
        Returns installation information for a given packet and a given path

        :param packet_name: Name of the packet like root, jana, etc
        :type packet_name: str
        :param install_path: Path of the packet installation
        :type install_path: str

        """
        installs = self.get_installs(packet_name)
        install_path = os.path.normpath(install_path)

        # Search for existing installation with this installation path
        for install in installs:
            # We compare it just by == as all saved installs have gone through os.path.normpath
            assert isinstance(install, dict)
            if install[INSTALL_PATH] == to_unicode(install_path):
                return install
        return None

    def update_install(self, packet_name, install_path, updating_data):
        """
        :param updating_data: A dict with data to update
        :type updating_data: dict
        :param packet_name: Name of the packet. Like root, genfit, rave, etc
        :param install_path: Path of the installation
        :return:
        """

        # normalize the path
        install_path = os.path.normpath(install_path)

        # Search for existing installation with this installation path
        existing_install = self.get_install(packet_name, install_path)

        # If we didn't find an install, lets add a new one
        if existing_install is None:
            existing_install = {}
            installs = self.get_installs(packet_name)
            installs.append(existing_install)
            existing_install[IS_ACTIVE] = True      # It is the first installation. Should be active
            existing_install[IS_OWNED] = False      # Nothing known about it, so guess we are not

        # if updating_data has IS_ACTIVE flag set to True, We have to uncheck all other our packets
        if updating_data.get(IS_ACTIVE, False):
            for install in self.get_installs(packet_name):
                # We compare it just by == as all saved installs have gone through os.path.normpath
                assert isinstance(install, dict)
                install[IS_ACTIVE] = False

        # set selected and ownership
        existing_install[INSTALL_PATH] = install_path
        existing_install.update(updating_data)
        return existing_install

    def remove_install(self, packet_name, install_path):
        """

        :param packet_name: Name of the packet. Like root, genfit, rave, etc
        :param install_path: Path of the installation
        :return:
        """

        installs = self.get_installs(packet_name)
        install_path = os.path.normpath(install_path)

        # Search for existing installation with this installation path
        existing_install = None
        for install in installs:
            # We compare it just by == as all saved installs have gone through os.path.normpath
            assert isinstance(install, dict)
            if install[INSTALL_PATH] == to_unicode(install_path):
                installs.remove(install)

    @property
    def top_dir(self):
        return self.data["top_dir"]

    @top_dir.setter
    def top_dir(self, path):
        self.data["top_dir"] = path

    def _update_schema(self):
        """Do migration between different DB schema versions"""

        # version 1 to 2 migration
        if self.data['file_version'] == 1:
            # Remove some fields:
            # (Why pop https://stackoverflow.com/questions/11277432/how-to-remove-a-key-from-a-python-dictionary)

            # installed group (we use packet/installs instead)
            self.data.pop('installed', None)

            # 'required' (we use dependency chain instead)
            for name, packet in self.data['packets'].items():
                if 'required' in packet:
                    packet.pop('required', None)

            # finally change the version
            self.data['file_version'] = 2   # No changes needed to update from v 1 to 2
            pass

