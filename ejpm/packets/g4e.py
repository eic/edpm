"""
This file provides information of how to build and configure Geant4 framework:
https://gitlab.com/jlab-eic/g4e.git


"""

import os

from ejpm.engine.commands import run, workdir
from ejpm.engine.env_gen import Set, Append, Prepend
from ejpm.engine.installation import PacketInstallationInstruction


class GeantInstallation(PacketInstallationInstruction):
    """Provides data for building and installing Geant4 framework
    source_path  = {app_path}/src/{version}          # Where the sources for the current version are located
    build_path   = {app_path}/build/{version}        # Where sources are built. Kind of temporary dir
    install_path = {app_path}/root-{version}         # Where the binary installation is
    """


    def __init__(self, default_tag='master', build_threads=8):
        """
        Installs Genfit track fitting framework
        """

        # Set initial values for parent class and self
        super(GeantInstallation, self).__init__('g4e')
        self.build_threads = build_threads
        self.clone_command = ''             # is set during self.setup(...)
        self.build_cmd = ''                 # is set during self.setup(...)
        self.required_deps = ['clhep', 'root', 'hepmc', 'geant', 'vgm']

    def setup(self, app_path):
        """Sets all variables like source dirs, build dirs, etc"""

        # We don't care about tags and have only 1 branch name
        branch = 'master'

        #
        # use_common_dirs_scheme sets standard package variables:
        # source_path  = {app_path} / src   / {branch}       # Where the sources for the current version are located
        # build_path   = {app_path} / build / {branch}       # Where sources are built. Kind of temporary dir
        # install_path = {app_path} / geant-{branch}         # Where the binary installation is
        self.use_common_dirs_scheme(app_path, branch)

        #
        # JANA download link. Clone with shallow copy
        # TODO accept version tuple to get exact branch
        self.clone_command = "git clone --depth 1 -b {branch} https://gitlab.com/jlab-eic/g4e.git {source_path}"\
            .format(branch=branch, source_path=self.source_path)

        # cmake command:
        # the  -Wno-dev  flag is to ignore the project developers cmake warnings for policy CMP0075
        self.build_cmd = "cmake -Wno-dev -DCMAKE_INSTALL_PREFIX={install_path} {source_path}" \
                         "&& cmake --build . -- -j {build_threads}" \
                         "&& cmake --build . --target install" \
                         .format(
                             source_path=self.source_path,    # cmake source
                             install_path=self.install_path,  # Installation path
                             build_threads=self.build_threads)     # make global options like '-j8'. Skip now

        # requirments  env var to locate
        # xerces-c     XERCESCROOT
        # ROOT         ROOTSYS
        # CCDB         CCDB_HOME
        # curl         CURL_HOME

    def step_install(self):
        self.step_clone()
        self.step_build()

    def step_clone(self):
        """Clones JANA from github mirror"""

        # Check the directory exists and not empty
        if os.path.exists(self.source_path) and os.path.isdir(self.source_path) and os.listdir(self.source_path):
            # The directory exists and is not empty. Nothing to do
            return
        else:
            # Create the directory
            run('mkdir -p {}'.format(self.source_path))

        # Execute git clone command
        run(self.clone_command)

    def step_build(self):
        """Builds JANA from the ground"""

        # Create build directory
        run('mkdir -p {}'.format(self.build_path))

        # go to our build directory
        workdir(self.build_path)

        # run scons && scons install
        run(self.build_cmd)

    def step_reinstall(self):
        """Delete everything and start over"""

        # clear sources directories if needed
        run('rm -rf {}'.format(self.app_path))

        # Now run build root
        self.step_install()

    @staticmethod
    def gen_env(data):
        """Generates environments to be set"""

        bin_path = os.path.join(data['install_path'], 'bin')
        yield Prepend('PATH', bin_path)  # to make available clhep-config and others


    #
    # OS dependencies are a map of software packets installed by os maintainers
    # The map should be in form:
    # os_dependencies = { 'required': {'ubuntu': "space separated packet names", 'fedora': "..."},
    #                     'optional': {'ubuntu': "space separated packet names", 'fedora': "..."}
    # The idea behind is to generate easy to use instructions: 'sudo apt-get install ... ... ... '
    os_dependencies = {
        'required': {
            'ubuntu': "",
            'fedora': ""
        },
        'optional': {
            'ubuntu': "",
            'fedora': ""
        },
    }