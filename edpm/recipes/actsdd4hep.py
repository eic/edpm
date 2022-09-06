"""
Acts dd4hep project
https://github.com/acts-project/acts-dd4hep
"""

import os

from edpm.engine.env_gen import Set, Append, Prepend
from edpm.engine.git_cmake_recipe import GitCmakeRecipe


class ActsDD4Hep(GitCmakeRecipe):
    """Provides data for building and installing Catch2 unit testing
    source_path  = {app_path}/src/{version}          # Where the sources for the current version are located
    build_path   = {app_path}/build/{version}        # Where sources are built. Kind of temporary dir
    install_path = {app_path}/root-{version}         # Where the binary installation is
    """

    def __init__(self):
        """
        Installs Genfit track fitting framework
        """

        # Set initial values for parent class and self
        super(ActsDD4Hep, self).__init__('actsdd4hep')                          # This name will be used in edpm commands
        self.config['branch'] = 'v1.0.1'                                        # The branch or tag to be cloned (-b flag)
        self.required_deps = ['acts']
        self.config['repo_address'] = 'https://github.com/acts-project/acts-dd4hep.git'      # Repo address
        self.config['cxx_standard'] = 17

    @staticmethod
    def gen_env(data):
        """Generates environments to be set"""
        path = data['install_path']

        import platform
        if platform.system() == 'Darwin':
            yield Append('DYLD_LIBRARY_PATH', os.path.join(path, 'lib'))

        yield Append('LD_LIBRARY_PATH', os.path.join(path, 'lib'))
        yield Append('CMAKE_PREFIX_PATH', os.path.join(path, 'lib', 'cmake', 'ActsDD4hep'))




    #
    # OS dependencies are a map of software packets installed by os maintainers
    # The map should be in form:
    # os_dependencies = { 'required': {'ubuntu': "space separated packet names", 'centos': "..."},
    #                     'optional': {'ubuntu': "space separated packet names", 'centos': "..."}
    # The idea behind is to generate easy to use instructions: 'sudo apt-get install ... ... ... '
    os_dependencies = {}