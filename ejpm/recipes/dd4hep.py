"""
This file provides information of how to build and configure HepMC framework:
https://gitlab.cern.ch/hepmc/HepMC
"""

import os

from ejpm.engine.commands import run, workdir
from ejpm.engine.env_gen import Set, Append, Prepend
from ejpm.engine.git_cmake_recipe import GitCmakeRecipe



class DD4HEPRecipe(GitCmakeRecipe):
    """Provides data for building and installing HepMC framework
    source_path  = {app_path}/src/{version}          # Where the sources for the current version are located
    build_path   = {app_path}/build/{version}        # Where sources are built. Kind of temporary dir
    install_path = {app_path}/root-{version}         # Where the binary installation is
    """

    def __init__(self):
        """
        Installs Genfit track fitting framework
        """

        # Set initial values for parent class and self
        super(DD4HEPRecipe, self).__init__('dd4hep')

        self.config['branch'] = 'v01-16'
        self.config['repo_address'] = 'https://github.com/AIDASoft/DD4hep.git'
        self.config['cmake_flags'] = ' -DDD4HEP_USE_GEANT4=ON -DDD4HEP_USE_LCIO=OFF '

    @staticmethod
    def gen_env(data):
        """Generates environments to be set"""

        install_path = data['install_path']
        bin_path = os.path.join(install_path, 'bin')
        yield Prepend('PATH', bin_path)  # to make available clhep-config and others
        yield Set('DD4HEP_DIR', install_path)

        yield Append('CMAKE_PREFIX_PATH', os.path.join(install_path, 'cmake'))
        yield Append('LD_LIBRARY_PATH', os.path.join(install_path, 'lib'))

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