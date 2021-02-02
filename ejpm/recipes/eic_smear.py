"""
This file provides information of how to build and configure Eic-smear framework:
https://gitlab.com/eic/eic-smear

"""

import os

from ejpm.engine.commands import run, workdir
from ejpm.engine.env_gen import Set, Append, Prepend
from ejpm.engine.git_cmake_recipe import GitCmakeRecipe


class EicSmearRecipe(GitCmakeRecipe):
    """Provides data for building and installing Genfit framework
    source_path  = {app_path}/src/{version}          # Where the sources for the current version are located
    build_path   = {app_path}/build/{version}        # Where sources are built. Kind of temporary dir
    install_path = {app_path}/root-{version}         # Where the binary installation is
    """

    def __init__(self):
        """"""
        # Set initial values for parent class and self
        super(EicSmearRecipe, self).__init__('eic-smear')
        self.clone_command = ''             # will be set by self.set_app_path
        self.build_cmd = ''                 # will be set by self.set_app_path
        self.required_deps = ['root']
        self.config['branch'] = '1.1.2'
        self.config['repo_address'] = 'https://gitlab.com/eic/eic-smear.git'

    @staticmethod
    def gen_env(data):
        """Generates environments to be set"""

        install_path = data['install_path']
        yield Set('EIC_SMEAR_HOME', install_path)
        yield Append('ROOT_INCLUDE_PATH', os.path.join(install_path, '/include'))

        lib_path = os.path.join(install_path, 'lib')  # on some platforms
        lib64_path = os.path.join(install_path, 'lib64')  # on some platforms

        if os.path.isdir(lib64_path):
            yield Prepend('LD_LIBRARY_PATH', lib64_path)
        else:
            yield Prepend('LD_LIBRARY_PATH', lib_path)

    #
    # OS dependencies are a map of software packets installed by os maintainers
    # The map should be in form:
    # os_dependencies = { 'required': {'ubuntu': "space separated packet names", 'centos': "..."},
    #                     'optional': {'ubuntu': "space separated packet names", 'centos': "..."}
    # The idea behind is to generate easy to use instructions: 'sudo apt-get install ... ... ... '
    os_dependencies = {
        'required': {
            'ubuntu': "",
            'centos': ""
        },
        'optional': {
            'ubuntu': "",
            'centos': ""
        },
    }
