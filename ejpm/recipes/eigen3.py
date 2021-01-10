"""
This file provides information of how to build and configure Eigen3 packet:
https://gitlab.com/libeigen/eigen.git

"""

import os

from ejpm.engine.env_gen import Prepend, Set, Append
from ejpm.engine.git_cmake_recipe import GitCmakeRecipe


class EigenRecipe(GitCmakeRecipe):
    """Provides data for building and installing Eicgen3 framework"""

    def __init__(self):
        super(EigenRecipe, self).__init__('eigen3')
        self.config['branch'] = '3.3.8'
        self.config['repo_address'] = 'https://gitlab.com/libeigen/eigen.git'

    @staticmethod
    def gen_env(data):
        """Generates environments to be set"""
        path = data['install_path']

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
