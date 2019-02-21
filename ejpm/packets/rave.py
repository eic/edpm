import os

from ejpm.engine.env_gen import Set, Prepend
from side_packages import provide_click_framework

provide_click_framework()

from ejpm.engine.installation import PacketInstallationInstruction
from ejpm.engine.commands import run, env, workdir


class RaveInstallation(PacketInstallationInstruction):
    """Provides data for building and installing root

    PackageInstallationContext is located in installation.py and contains the next standard package variables:
    """

    def __init__(self, build_threads=8):
        # Call parent constructor to fill version, app_path ... and others
        # (!) it is called AFTER we override self.version
        super(RaveInstallation, self).__init__('rave')

        self.clone_command = ""
        self.bootstrap_command = ""         # This command is called after clone command
        self.build_command = ""
        self.build_threads = build_threads

    def setup(self, app_path):
        """Sets all variables like source dirs, build dirs, etc"""

        branch = 'master'
        #
        # use_common_dirs_scheme sets standard package variables:
        # version      = 'v{}-{:02}-{:02}'                 # Stringified version. Used to create directories and so on
        # source_path  = {app_path}/src/{version}          # Where the sources for the current version are located
        # build_path   = {app_path}/build/{version}        # Where sources are built. Kind of temporary dir
        # install_path = {app_path}/root-{version}         # Where the binary installation is
        self.use_common_dirs_scheme(app_path, branch)

        # ENV RAVEPATH $INSTALL_DIR_RAVE

        # JANA download link. Clone with shallow copy
        # TODO accept version tuple to get exact branch
        self.clone_command = "git clone --depth 1 -b {branch} https://github.com/WolfgangWaltenberger/rave.git {source_path}" \
            .format(branch=branch, source_path=self.source_path)

        self.bootstrap_command = './bootstrap'

        # cmake command:
        # the  -Wno-dev  flag is to ignore the project developers cmake warnings for policy CMP0075
        # (!) {{clhep_lib_dir}} and {{clhep_include_dir}} is in 2 braces. So it becomes {clhep_include_dir}
        #     on step_build the right environment will be set and we will use .format(..) again to fill them
        #     ugly? YEA!!! say hello to RAVE
        self.build_command = './configure --disable-java --prefix=$RAVEPATH ' \
                             ' LDFLAGS="-L{{clhep_lib_dir}}" ' \
                             ' CXXFLAGS="-std=c++11 -I{{clhep_include_dir}}" ' \
                             '&&   make -j{glb_make_options} install' \
                             "&& for f in $(ls $RAVEPATH/include/rave/*.h); do sed -i 's/RaveDllExport//g' $f; done" \
            .format(install_path=self.install_path,
                    glb_make_options="",
                    version=self.selected_tag)

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

        run(self.clone_command)         # Execute git clone command
        workdir(self.source_path)       # Go to our build directory
        run(self.bootstrap_command)     # This command required by rave once...

    def step_build(self):
        # Create build directory

        env('RAVEPATH', self.install_path)

        # Rave uses ./configure so we building it in {source_path}
        # go to our build directory
        workdir(self.source_path)

        # environment variables CLHEP_LIB_DIR and CLHEP_INCLUDE_DIR should be set at this stage to compile it
        # otherwise we fall back to default debian install location (RHEL7 doesn't have clep in its repo)
        clhep_lib_dir = os.environ.get('CLHEP_LIB_DIR', '/usr/lib')
        clhep_include_dir = os.environ.get('CLHEP_INCLUDE_DIR', '/usr/include')

        build_command_with_clhep = self.build_command.format(
            clhep_lib_dir=clhep_lib_dir,
            clhep_include_dir=clhep_include_dir)

        # run cmake && make && install
        run(build_command_with_clhep)

    @staticmethod
    def gen_env(data):
        install_path = data['install_path']

        yield Set('RAVEPATH', install_path)
        yield Prepend('CMAKE_PREFIX_PATH', os.path.join(install_path, 'share', 'rave'))
        yield Prepend('LD_LIBRARY_PATH', os.path.join(install_path, 'lib'))

    def step_set_env(self):
        """

        ENV LD_LIBRARY_PATH "$RAVEPATH/lib:$LD_LIBRARY_PATH"

        # May be pointless defining these. At least cmake reports that it is going
        # to try and build GenFit with RAVE support with these here (AND defined in the cmake commad!)
        ENV RAVE_CFLAGS "-g -O2"
        ENV RAVE_INCLUDE_DIRS $RAVEPATH/include
        ENV RAVE_LDFLAGS "-L$INSTALL_DIR_RAVE/lib -lRaveBase -lRaveCore -lRaveVertex -lRaveFlavorTag -lRaveVertexKinematics"

        """
