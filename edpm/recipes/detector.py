"""
EIC DD4Hep detector geometry files:
https://github.com/eic/ecce
https://github.com/eic/ip6

"""

import os
import sys
import platform

from edpm.engine.commands import run, workdir
from edpm.engine.env_gen import Set, Prepend
from edpm.engine.recipe import Recipe


class EcceDetectorRecipe(Recipe):
    """Provides data for building and installing Geant4 framework
    source_path  = {app_path}/src/{version}          # Where the sources for the current version are located
    build_path   = {app_path}/build/{version}        # Where sources are built. Kind of temporary dir
    install_path = {app_path}/root-{version}         # Where the binary installation is
    """


    def __init__(self):
        """ Installs Genfit track fitting framework """

        # Set initial values for parent class and self
        super(EcceDetectorRecipe, self).__init__('detector')
        self.clone_command = ''             # is set during self.setup(...)
        self.build_cmd = ''                 # is set during self.setup(...)
        self.config['branch'] = 'main'
        self.config['branch_ecce'] = self.config['branch']
        self.config['branch_ip6'] = 'master'    # https://github.com/eic/ip6/issues/1
        self.required_deps = ['clhep', 'root', 'hepmc3', 'dd4hep', 'acts']
        self.config['repo_address_ecce'] = 'https://github.com/eic/ecce'
        self.config['repo_address_ip6'] = 'https://github.com/eic/ip6'

    def setup(self, db):
        """Sets all variables like source dirs, build dirs, etc"""

        #
        # Git download link. Clone with shallow copy
        self.config['source_path_ecce'] = "{app_path}/{branch}/ecce".format(**self.config)
        self.config['source_path_ip6'] = "{app_path}/{branch}/ip6".format(**self.config)

        # The directory for cmake build
        self.config['build_path_ecce'] = "{app_path}/{branch}/ecce/cmake-build-debug".format(**self.config)
        self.config['build_path_ip6'] = "{app_path}/{branch}/ip6/cmake-build-debug".format(**self.config)

        self.config['install_path_ecce'] = "{app_path}/{branch}/compiled/ecce".format(**self.config)
        self.config['install_path_ip6'] = "{app_path}/{branch}/compiled/ip6".format(**self.config)

        self.config['clone_command_ecce'] = "git clone -b {branch_ecce} {repo_address_ecce} {source_path_ecce}"\
            .format(**self.config)
        self.config['clone_command_ip6'] = "git clone -b {branch_ip6} {repo_address_ip6} {source_path_ip6}" \
            .format(**self.config)

        # Because in general we await install_path to be set to something
        self.config['install_path'] = self.config['install_path_ecce']

        # Link ip6 repo to ecce, as IP6 should be linked to installed ECCE
        self.config['ip6_link_source'] = "{install_path_ip6}/share/ip6".format(**self.config)
        self.config['ip6_link_target'] = "{install_path_ecce}/share/ecce/ip6".format(**self.config)

        # cmake command:
        # the  -Wno-dev  flag is to ignore the project developers cmake warnings for policy CMP0075
        self.config['build_cmd_ecce'] = "cmake -w -DCMAKE_INSTALL_PREFIX={install_path_ecce} -DCMAKE_CXX_STANDARD={cxx_standard} {source_path_ecce}" \
                         "&& cmake --build . -- -j {build_threads}" \
                         "&& cmake --build . --target install" \
                         .format(**self.config)
        self.config['build_cmd_ip6'] = "cmake -w -DCMAKE_INSTALL_PREFIX={install_path_ip6} -DCMAKE_CXX_STANDARD={cxx_standard} {source_path_ip6}" \
                         "&& cmake --build . -- -j {build_threads}" \
                         "&& cmake --build . --target install" \
                         .format(**self.config)

    def step_install(self):
        self.step_clone()
        self.step_build()

    def step_clone(self):
        """Clones JANA from github mirror"""

        # Check the directory exists and not empty
        source_ecce = self.config['source_path_ecce']
        source_ip6 = self.config['source_path_ip6']

        # Check ECCE directory not exists or empty
        if not (os.path.exists(source_ecce) and os.path.isdir(source_ecce) and os.listdir(source_ecce)):
            run('mkdir -p {}'.format(source_ecce))   # Create the directory
            run(self.config['clone_command_ecce'])   # Execute git clone command

        # Check ip6 directory not exists or empty
        if not (os.path.exists(source_ip6) and os.path.isdir(source_ip6) and os.listdir(source_ip6)):

            run('mkdir -p {}'.format(source_ip6))    # Create the directory
            run(self.config['clone_command_ip6'])    # Execute git clone command

    @staticmethod
    def build(build_path, build_cmd):
        """Builds JANA from the ground"""

        # Create build directory
        run('mkdir -p {}'.format(build_path))

        # go to our build directory
        workdir(build_path)

        # run scons && scons install
        run(build_cmd)

    def step_build(self):
        """Builds detectors from the ground"""

        # Create build directory
        self.build(self.config['build_path_ip6'], self.config['build_cmd_ip6'])
        self.build(self.config['build_path_ecce'], self.config['build_cmd_ecce'])

        # Link ip6 repo to ecce
        if os.path.islink(self.config['ip6_link_target']):
            run("unlink {ip6_link_target}".format(**self.config))
        run("ln -s {ip6_link_source} {ip6_link_target}".format(**self.config))


    def step_reinstall(self):
        """Delete everything and start over"""

        # clear sources directories if needed
        run('rm -rf {}'.format(self.app_path))

        # Now run build root
        self.step_install()

    @staticmethod
    def gen_env(data):
        """Generates environments to be set"""

        install_path = os.path.join(data['install_path'], 'share/ecce/')

        yield Set('DETECTOR_PATH', install_path)

        if platform.system() == 'Darwin':
            yield Prepend('DYLD_LIBRARY_PATH', os.path.join(install_path, 'lib'))

        yield Prepend('LD_LIBRARY_PATH', os.path.join(install_path, 'lib'))


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