# This file contain classes that holds packet installation instructions
# Most notorious are:
#  run      - Runs an OS command ,
#  workdir  - Changes working directory,
#  env      - Sets environment variable


import os
import subprocess
import sys
import inspect

_abi_name = ""


def get_abi_name():
    """Returns the name for resulting ABI, like Ubuntu """

    global _abi_name
    if not _abi_name:
        result = subprocess.Popen(['perl', 'osrelease.pl'], stdout=subprocess.PIPE, stderr=sys.stderr).communicate()
        _abi_name = result[0].decode('utf-8').strip()
    return _abi_name


def get_jepm_path():
    """Returns the path (the directory path) of jepm scripts"""

    file_path = inspect.stack()[0][1]
    file_dir = os.path.dirname(file_path)
    return file_dir

class Context:
    # installation dir
    work_dir = ""

    prerequesties = {
        "ubuntu": ["python3-pip, scons, cmake"]
    }

    commands = []

    total_executed_commands = []

    @staticmethod
    def print_self():
        # work_dir
        click.secho("work_dir      :", fg='blue', nl=False)
        click.secho(Context.work_dir)


class PackageInstallationContext:
    """This class stores information which is pretty similar for each package (like directory structure)

    The important here is that while we try to stick to this naming, each package can override them if needed

    """

    def __init__(self, app_name, version_tuple):
        #
        # Root clone branch is like v6-14-04 so we format binary version accordingly
        self.version = 'v{}-{:02}-{:02}'.format(*version_tuple)  # v6-14-04

        #
        # Root general installation directory
        self.app_path = "{glb_app_path}/{app_name}" \
            .format(glb_app_path=Context.work_dir, app_name=app_name)

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
            .format(app_path=self.app_path, app_name=self.app_name, version=self.version)

