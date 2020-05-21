"""
This file provides information of how to build and configure Delphes packet:
https://github.com/delphes/delphes.git

"""

import os

from ejpm.engine.env_gen import Prepend, Set, Append
from ejpm.engine.git_cmake_recipe import GitCmakeRecipe


class DelphesRecipe(GitCmakeRecipe):
    """Provides data for building and installing Delphes fast simulation framework"""

    def __init__(self):
        super(DelphesRecipe, self).__init__('delphes')
        self.config['branch'] = '3.4.2'
        self.config['repo_address'] = 'https://github.com/delphes/delphes.git'

    @staticmethod
    def gen_env(data):
        """Generates environments to be set"""
        path = data['install_path']

        yield Set("DELPHES_HOME", path)
        yield Prepend('CMAKE_PREFIX_PATH', os.path.join(path, 'share/eigen3/cmake/'))

    #
    # OS dependencies are a map of software packets installed by os maintainers
    # The map should be in form:
    # os_dependencies = { 'required': {'ubuntu': "space separated packet names", 'centos': "..."},
    #                     'optional': {'ubuntu': "space separated packet names", 'centos': "..."}
    # The idea behind is to generate easy to use instructions: 'sudo apt-get install ... ... ... '
    os_dependencies = {
        'required': {
            'ubuntu': "",
            'centos': "",
            'centos8': ""
        },
        'optional': {
            'ubuntu': "",
            'centos': ""
        },
    }
