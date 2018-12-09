# This module contains classes, which hold information about how to install packets


class PacketInstallationInstruction(object):
    """
    This class stores information which is pretty similar for each package (like directory structure)

    The important here is that while we try to stick to this naming, each package can override them if needed

    """

    def __init__(self, name, app_path, version_tuple):

        #
        # Short lowercase name of a packet
        self.name = name

        #
        # Root clone branch is like v6-14-04 so we format binary version accordingly
        self.version = 'v{}-{:02}-{:02}'.format(*version_tuple)  # v6-14-04

        #
        # Root general installation directory
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
