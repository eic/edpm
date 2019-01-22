# This module contains classes, which hold information about how to install packets


class PacketInstallationInstruction(object):
    """
    This class stores information which is pretty similar for each package (like directory structure)

    The important here is that while we try to stick to this naming, each package can override them if needed

    Usually this class is used like:

    # packets/my_packet.py file:

    MyPacketInstallationInstruction(PacketInstallationInstruction):
        # ... define your packet installation instruction by
        # defining:

        def set_app_path(...)  # - function that setups variables when the installation path is known

        # and logic with
        def step_install(...)  # - installs application
        def step_download(...) # - downloads from network
        def step...

    # usage of MyPacketInstallationInstruction is like:




    """

    def __init__(self, name, version):
        #
        # Short lowercase name of a packet
        self.name = name

        #
        # version could be given as a tuple (6, 06, 15) or some string 'master'
        if isinstance(version, tuple):
            self.version_tuple = version
            self.version = 'v{}-{:02}-{:02}'.format(*version)
        else:
            self.version_tuple = None
            self.version = version

        #
        # Next variables are set by ancestors
        self.app_path = ""          # installation path of this packet, all other pathes relative to this
        self.download_path = ""     # where we download the source or clone git
        self.source_path = ""       # The directory with source files for current version
        self.build_path = ""        # The directory for cmake/scons build
        self.install_path = ""      # The directory, where binary is installed
        self.required_deps = []     # Packets which are required for this to run
        self.optional_deps = []     # Optional packets

    def set_app_path(self, app_path):
        """This function is used to format and fill variables, when app_path is known download command"""
        # ... (!) inherited classes should implement its logic here
        raise NotImplementedError()

    def use_common_dirs_scheme(self, app_path):
        """Function sets common directory scheme. It is the same for many packets:

        """

        self.app_path = app_path

        #
        # where we download the source or clone git
        self.download_path = "{app_path}/src" \
            .format(app_path=self.app_path)

        #
        # The directory with source files for current version
        self.source_path = "{app_path}/src/{version}" \
            .format(app_path=self.app_path, version=self.version)

        #
        # The directory for cmake build
        self.build_path = "{app_path}/build/{version}" \
            .format(app_path=self.app_path, version=self.version)

        #
        # The directory, where binary is installed
        self.install_path = "{app_path}/{app_name}-{version}" \
            .format(app_path=self.app_path, app_name=self.name, version=self.version)

    def step_install(self):
        """Installs application"""
        raise NotImplementedError()


