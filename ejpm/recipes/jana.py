"""
This file provides information of how to build and configure JANA2 packet:
https://github.com/JeffersonLab/JANA2

"""

import os

from ejpm.engine.commands import run, workdir, env
from ejpm.engine.env_gen import Prepend, Set, Append
from ejpm.engine.git_cmake_recipe import GitCmakeRecipe
from ejpm.engine.recipe import Recipe


class JanaRecipe(GitCmakeRecipe):
    """Provides data for building and installing JANA2 framework

    PacketInstallationInstruction is located in recipe.py and contains the next standard package variables:


    source_path  = {app_path}/src/{version}          # Where the sources for the current version are located
    build_path   = {app_path}/build/{version}        # Where sources are built. Kind of temporary dir
    install_path = {app_path}/root-{version}         # Where the binary installation is
    """

    def __init__(self):
        super(JanaRecipe, self).__init__('jana')
        self.config['branch'] = 'v2.0.3'
        self.config['repo_address'] = 'https://github.com/JeffersonLab/JANA2.git'

    @staticmethod
    def gen_env(data):
        """Generates environments to be set"""

        install_path = data['install_path']

        yield Set('JANA_HOME', install_path)
        yield Append('JANA_PLUGIN_PATH', '$JANA_HOME/plugins')
        yield Prepend('PATH', '$JANA_HOME/bin')

    #
    # OS dependencies are a map of software packets installed by os maintainers
    # The map should be in form:
    # os_dependencies = { 'required': {'ubuntu': "space separated packet names", 'centos': "..."},
    #                     'optional': {'ubuntu': "space separated packet names", 'centos': "..."}
    # The idea behind is to generate easy to use instructions: 'sudo apt-get install ... ... ... '
    os_dependencies = {
        'required': {
            'ubuntu': "scons libxerces-c-dev curl python3-dev",
            'centos': "scons xerces-c-devel curl",
            'centos8': "python3-scons xerces-c-devel curl"
        },
        'optional': {
            'ubuntu': "",
            'centos': ""
        },
    }
