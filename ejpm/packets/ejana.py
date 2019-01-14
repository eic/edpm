"""
https://github.com/JeffersonLab/JANA.git
export BMS_OSNAME=`./SBMS/osrelease.pl`

"""

import os

from ejpm.engine.installation import PacketInstallationInstruction
from ejpm.engine.commands import run, env, workdir


class EjanaInstallation(PacketInstallationInstruction):
    """Provides data for building and installing JANA framework

    PackageInstallationContext is located in installation.py and contains the next standard package variables:

    version      = 'v{}-{:02}-{:02}'                 # Stringified version. Used to create directories and so on
    glb_app_path = Context.work_dir                  # The directory where all other packets are installed
    source_path  = {app_path}/src/{version}          # Where the sources for the current version are located
    build_path   = {app_path}/build/{version}        # Where sources are built. Kind of temporary dir
    install_path = {app_path}/root-{version}         # Where the binary installation is
    """

    fedora_required_packets = ""
    fedora_optional_packets = ""
    ubuntu_required_packets = ""
    ubuntu_optional_packets = ""

    def __init__(self, version='dmitry_dev', build_threads=8):
        """

        :param version: Root version
        """

        # Set initial values for parent class and self
        super(EjanaInstallation, self).__init__('ejana', version)
        self.build_threads = build_threads
        self.clone_command = ""
        self.build_command = ""

    def set_app_path(self, app_path):
        """Sets all variables like source dirs, build dirs, etc"""

        #
        # use_common_dirs_scheme sets standard package variables:
        # version      = 'v{}-{:02}-{:02}'                 # Stringified version. Used to create directories and so on
        # source_path  = {app_path}/src/{version}          # Where the sources for the current version are located
        # build_path   = {app_path}/build/{version}        # Where sources are built. Kind of temporary dir
        # install_path = {app_path}/root-{version}         # Where the binary installation is
        self.use_common_dirs_scheme(app_path)

        #
        # JANA download link. Clone with shallow copy
        # TODO accept version tuple to get exact branch
        self.clone_command = "git clone --depth 1 -b {branch} https://gitlab.com/eic/ejana.git {source_path}"\
            .format(branch=self.version, source_path=self.source_path)

        #
        # scons installation command:
        self.build_command = "scons install -j{build_threads} PREFIX={install_path} VARIANT-DIR={build_path} && scons install"\
                         .format(build_threads=self.build_threads,
                                 install_path=self.install_path,
                                 build_path=self.build_path)

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

        # go to source directory to invoke scons
        workdir(os.path.join(self.source_path, "src"))

        # run scons && scons install
        run(self.build_command)

    def step_reinstall(self):
        """Delete everything and start over"""

        # clear sources directories if needed
        run('rm -rf {}'.format(self.app_path))

        # Now run build root
        self.step_install()