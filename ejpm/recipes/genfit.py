"""
This file provides information of how to build and configure Genfit framework:
https://github.com/GenFit/GenFit
"""

import os

from ejpm.engine.env_gen import Set, Append, Prepend
from ejpm.engine.git_cmake_recipe import GitCmakeRecipe


class GenfitRecipe(GitCmakeRecipe):
    """Provides data for building and installing Genfit framework
    source_path  = {app_path}/src/{version}          # Where the sources for the current version are located
    build_path   = {app_path}/build/{version}        # Where sources are built. Kind of temporary dir
    install_path = {app_path}/root-{version}         # Where the binary installation is
    """

    def __init__(self):
        """
        Installs Genfit track fitting framework
        """

        # Set initial values for parent class and self
        super(GenfitRecipe, self).__init__('genfit')                        # This name will be used in ejpm commands
        self.config['branch'] = '02-00-00'                                    # The branch or tag to be cloned (-b flag)
        self.config['repo_address'] = 'https://github.com/GenFit/GenFit.git'    # Repo address
        self.required_deps = ['eigen3', 'clhep', 'root']


    @staticmethod
    def gen_env(data):
        """Generates environments to be set"""
        path = data['install_path']

        yield Set('GENFIT', path)
        yield Set('GENFIT_DIR', path)

        # it could be lib or lib64. There are bugs on different platforms (RHEL&centos and WSL included)
        # https://stackoverflow.com/questions/46847939/config-site-for-vendor-libs-on-centos-x86-64
        # https: // bugzilla.redhat.com / show_bug.cgi?id = 1510073

        import platform
        if platform.system() == 'Darwin':
            yield Append('DYLD_LIBRARY_PATH', os.path.join(path, 'lib'))
            yield Append('DYLD_LIBRARY_PATH', os.path.join(path, 'lib64'))

        yield Append('LD_LIBRARY_PATH', os.path.join(path, 'lib'))
        yield Append('LD_LIBRARY_PATH', os.path.join(path, 'lib64'))

    #
    # OS dependencies are a map of software packets installed by os maintainers
    # The map should be in form:
    # os_dependencies = { 'required': {'ubuntu': "space separated packet names", 'centos': "..."},
    #                     'optional': {'ubuntu': "space separated packet names", 'centos': "..."}
    # The idea behind is to generate easy to use instructions: 'sudo apt-get install ... ... ... '
    os_dependencies = {
        'required': {
            'ubuntu': "libboost-dev libeigen3-dev",
            'centos': "boost-devel eigen3-devel",
            'centos8': "boost-devel eigen3-devel",
        },
        'optional': {
            'ubuntu': "",
            'centos': ""
        },
    }