"""
This file provides information of how to build and configure Eigen3 packet:
https://gitlab.com/libeigen/eigen.git

"""

import os

from edpm.engine.commands import run
from edpm.engine.env_gen import Prepend, Set, Append
from edpm.engine.git_cmake_recipe import GitCmakeRecipe
import edpm

class EcceDetectorRecipe(GitCmakeRecipe):
    """Provides data for building and installing Eicgen3 framework"""

    def __init__(self):
        super(EcceDetectorRecipe, self).__init__('ecce')
        self.config['branch'] = 'master'
        self.config['repo_address'] = 'https://github.com/eic/ecce'

    def setup(self, pdb):
        """Sets all variables like source dirs, build dirs, etc"""
        assert isinstance(pdb, edpm.engine.db.PacketStateDatabase)
        super(EcceDetectorRecipe, self).setup(pdb)
        #print()
        self.config['install_path_ip6'] = pdb.get_active_install('ip6')['install_path']


    def step_build(self):
        super(EcceDetectorRecipe, self).step_build()
        run('ln -s {install_path_ip6}/share/ip6/ip6 {install_path}/share/ecce/ip6')

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
