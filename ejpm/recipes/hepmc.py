"""
This file provides information of how to build and configure HepMC framework:
https://gitlab.cern.ch/hepmc/HepMC


"""

import os

from ejpm.engine.commands import run, workdir
from ejpm.engine.env_gen import Set, Append, Prepend
from ejpm.engine.git_cmake_recipe import GitCmakeRecipe



class HepMCRecipe(GitCmakeRecipe):
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
        super(HepMCRecipe, self).__init__('hepmc')

        self.config['branch'] = 'HEPMC_02_06_09'
        self.config['repo_address'] = 'https://gitlab.cern.ch/hepmc/HepMC.git'
        self.config['cmake_flags'] = ' -Dmomentum:STRING=GEV -Dlength:STRING=MM '

    @staticmethod
    def gen_env(data):
        """Generates environments to be set"""

        install_path = data['install_path']
        bin_path = os.path.join(install_path, 'bin')
        yield Prepend('PATH', bin_path)  # to make available clhep-config and others
        yield Set('HEPMC_DIR', install_path)

        import platform
        if platform.system() == 'Darwin':
            yield Append('DYLD_LIBRARY_PATH', os.path.join(install_path, 'lib'))
            yield Append('DYLD_LIBRARY_PATH', os.path.join(install_path, 'lib64'))

        yield Append('LD_LIBRARY_PATH', os.path.join(install_path, 'lib'))
        yield Append('LD_LIBRARY_PATH', os.path.join(install_path, 'lib64'))

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