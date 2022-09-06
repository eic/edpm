"""
EIC DD4Hep detector geometry files:
https://github.com/eic/epic
https://github.com/eic/ip6

"""

import os
import sys
import platform

from edpm.engine.commands import run, workdir
from edpm.engine.env_gen import Set, Prepend
from edpm.engine.recipe import Recipe


class EpicDetectorRecipe(Recipe):
    """Provides data for building and installing Geant4 framework
    source_path  = {app_path}/src/{version}          # Where the sources for the current version are located
    build_path   = {app_path}/build/{version}        # Where sources are built. Kind of temporary dir
    install_path = {app_path}/root-{version}         # Where the binary installation is
    """


    def __init__(self):
        """ Installs EPIC detector DD4Hep geometry """

        # Set initial values for parent class and self
        super(EpicDetectorRecipe, self).__init__('detector')
        self.clone_command = ''             # is set during self.setup(...)
        self.build_cmd = ''                 # is set during self.setup(...)
        self.config['branch'] = 'main'
        self.config['branch_epic'] = self.config['branch']
        self.config['branch_ip6'] = 'master'    # https://github.com/eic/ip6/issues/1
        self.required_deps = ['clhep', 'eigen3', 'root', 'hepmc3', 'podio', 'edm4hep', 'eicd', 'geant4','dd4hep', 'acts', 'actsdd4hep' ]
        self.config['repo_address_epic'] = 'https://github.com/eic/epic'
        self.config['repo_address_ip6'] = 'https://github.com/eic/ip6'

    def setup(self, db):
        """Sets all variables like source dirs, build dirs, etc"""

        #
        # Git download link. Clone with shallow copy
        self.config['source_path_epic'] = "{app_path}/{branch}/epic".format(**self.config)
        self.config['source_path_ip6'] = "{app_path}/{branch}/ip6".format(**self.config)

        # The directory for cmake build
        self.config['build_path_epic'] = "{app_path}/{branch}/epic/cmake-build-debug".format(**self.config)
        self.config['build_path_ip6'] = "{app_path}/{branch}/ip6/cmake-build-debug".format(**self.config)

        self.config['install_path_epic'] = "{app_path}/{branch}/compiled/epic".format(**self.config)
        self.config['install_path_ip6'] = "{app_path}/{branch}/compiled/ip6".format(**self.config)

        self.config['clone_command_epic'] = "git clone -b {branch_epic} {repo_address_epic} {source_path_epic}"\
            .format(**self.config)
        self.config['clone_command_ip6'] = "git clone -b {branch_ip6} {repo_address_ip6} {source_path_ip6}" \
            .format(**self.config)

        # Because in general we await install_path to be set to something
        self.config['install_path'] = self.config['install_path_epic']

        # Link ip6 repo to epic, as IP6 should be linked to installed epic
        self.config['ip6_link_source'] = "{install_path_ip6}/share/ip6/ip6".format(**self.config)
        self.config['ip6_link_target'] = "{install_path_epic}/share/epic/ip6".format(**self.config)

        # cmake command:
        # the  -Wno-dev  flag is to ignore the project developers cmake warnings for policy CMP0075
        self.config['build_cmd_epic'] = "cmake -DCMAKE_INSTALL_PREFIX={install_path_epic} -DCMAKE_CXX_STANDARD={cxx_standard} {source_path_epic}" \
                         "&& cmake --build . -- -j {build_threads}" \
                         "&& cmake --build . --target install" \
                         .format(**self.config)
        self.config['build_cmd_ip6'] = "cmake -DCMAKE_INSTALL_PREFIX={install_path_ip6} -DCMAKE_CXX_STANDARD={cxx_standard} {source_path_ip6}" \
                         "&& cmake --build . -- -j {build_threads}" \
                         "&& cmake --build . --target install" \
                         .format(**self.config)

    def step_install(self):
        self.step_clone()
        self.step_build()

    def step_clone(self):
        """Clones JANA from github mirror"""

        # Check the directory exists and not empty
        source_epic = self.config['source_path_epic']
        source_ip6 = self.config['source_path_ip6']

        # Check epic directory not exists or empty
        if not (os.path.exists(source_epic) and os.path.isdir(source_epic) and os.listdir(source_epic)):
            run('mkdir -p {}'.format(source_epic))   # Create the directory
            run(self.config['clone_command_epic'])   # Execute git clone command

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
        self.build(self.config['build_path_epic'], self.config['build_cmd_epic'])

        # Link ip6 repo to epic
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

        if 'built_with_config' not in data:
            # The detector is not built yet, so we just skip it
            return

        install_path = data['built_with_config']['install_path_epic']
        # print(data)
        # exit(1)
        epic_lib_path = os.path.join(data['built_with_config']['install_path_epic'], 'lib')
        ip6_lib_path = os.path.join(data['built_with_config']['install_path_ip6'], 'lib')

        yield Set('DETECTOR_PATH', os.path.join(install_path, 'share', 'epic'))

        if platform.system() == 'Darwin':
            yield Prepend('DYLD_LIBRARY_PATH', epic_lib_path)
            yield Prepend('DYLD_LIBRARY_PATH', ip6_lib_path)

        yield Prepend('LD_LIBRARY_PATH', epic_lib_path)
        yield Prepend('LD_LIBRARY_PATH', ip6_lib_path)

        yield Set('EIC_DD4HEP_HOME', data['built_with_config']['install_path_epic'])
        yield Set('IP6_DD4HEP_HOME', data['built_with_config']['install_path_ip6'])

    #
    # OS dependencies are a map of software packets installed by os maintainers
    # The map should be in form:
    # os_dependencies = { 'required': {'ubuntu': "space separated packet names", 'centos': "..."},
    #                     'optional': {'ubuntu': "space separated packet names", 'centos': "..."}
    # The idea behind is to generate easy to use instructions: 'sudo apt-get install ... ... ... '
    os_dependencies = {}