"""
This file provides information of how to build and configure Geant4 framework:
https://github.com/Geant4


"""

import os
import platform

from ejpm.engine.commands import run, workdir
import ejpm.engine.env_gen as env_gen
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
        super(GeantInstallation, self).__init__('geant')
        self.build_threads = build_threads
        self.clone_command = ''             # will be set by self.set_app_path
        self.build_cmd = ''                 # will be set by self.set_app_path

    def setup(self, app_path):
        """Sets all variables like source dirs, build dirs, etc"""

        # We don't care about tags and have only 1 branch name
        branch = 'v10.5.0'

        #
        # use_common_dirs_scheme sets standard package variables:
        # source_path  = {app_path} / src   / {branch}       # Where the sources for the current version are located
        # build_path   = {app_path} / build / {branch}       # Where sources are built. Kind of temporary dir
        # install_path = {app_path} / geant-{branch}         # Where the binary installation is
        self.use_common_dirs_scheme(app_path, branch)

        #
        # JANA download link. Clone with shallow copy
        # TODO accept version tuple to get exact branch
        self.clone_command = "git clone --depth 1 -b {branch} https://github.com/Geant4/geant4 {source_path}"\
            .format(branch=branch, source_path=self.source_path)

        # cmake command:
        # the  -Wno-dev  flag is to ignore the project developers cmake warnings for policy CMP0075
        self.build_cmd = """
            cmake
                -DGEANT4_INSTALL_DATA=ON
                -DGEANT4_BUILD_CXXSTD=11
                -DGEANT4_USE_GDML=ON
                -DGEANT4_USE_SYSTEM_CLHEP=ON
                -DCLHEP_ROOT_DIR=$CLHEP
                -DGEANT4_USE_OPENGL_X11=ON
                -DGEANT4_USE_RAYTRACER_X11=ON
                -DGEANT4_BUILD_MULTITHREADED=ON 
                -DGEANT4_USE_QT=ON
                -DCMAKE_INSTALL_PREFIX={install_path}
                -Wno-dev
                {source_path}
            && cmake --build . -- -j {build_threads}
            && cmake --build . --target install"""\
                         .format(
                             source_path=self.source_path,    # cmake source
                             install_path=self.install_path,  # Installation path
                             build_threads=self.build_threads)     # make global options like '-j8'. Skip now
        # remove multiple spaces and \n
        self.build_cmd = " ".join(self.build_cmd.split())

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
        """Generates environments to be set

        This function is a bit more tricky, we are going to use RawText which actually allows to:
         1. wright a custom text for sh and csh environment scripts
         2. and run a python command to set the environment

        For bash and csh we want just to call 'source .../geant4.sh[csh]'
        But we also want to set something for python to build Geant from scratch (when no geant4.sh[csh] yet)
        update_python_environment - subfunction do this

        """

        install_path = data['install_path']
        bin_path = os.path.join(install_path, 'bin')
        lib_path = os.path.join(install_path, 'lib')        # on some platforms
        lib64_path = os.path.join(install_path, 'lib64')    # on some platforms

        def update_python_environment():
            """Function that will update Geant environment in python
            We need this function because we DON'T want source thisroot in python
            """
            env_updates = [
                env_gen.Append('LD_LIBRARY_PATH', lib_path),
                env_gen.Append('LD_LIBRARY_PATH', lib64_path)
            ]

            if platform.system() == 'Darwin':
                env_updates.append(env_gen.Append('DYLD_LIBRARY_PATH', lib_path))
                env_updates.append(env_gen.Append('DYLD_LIBRARY_PATH', lib64_path))

            for updater in env_updates:
                updater.update_python_env()

        # We just call thisroot.xx in different shells

        yield Prepend('PATH', bin_path)  # to make available clhep-config and others

        sh_text = "source {}".format(os.path.join(bin_path, 'geant4.sh'))

        # in Geant CSH script Geant asks to get a path for geant bin directory
        csh_text = "source {} {}".format(os.path.join(bin_path, 'geant4.csh'), bin_path)

        yield env_gen.RawText(
            sh_text,
            csh_text,
            update_python_environment
        )

    #
    # OS dependencies are a map of software packets installed by os maintainers
    # The map should be in form:
    # os_dependencies = { 'required': {'ubuntu': "space separated packet names", 'centos': "..."},
    #                     'optional': {'ubuntu': "space separated packet names", 'centos': "..."}
    # The idea behind is to generate easy to use instructions: 'sudo apt-get install ... ... ... '
    os_dependencies = {
        'required': {
            'ubuntu': "libxerces-c3-dev libexpat-dev qtbase5-dev libqt5opengl5-dev libxmu-dev libx11-dev",
            'centos': "assimp-devel expat-devel libX11-devel libXt-devel libXmu-devel libXrender-devel libXpm-devel"
                      "libXft-devel libAfterImage libAfterImage-devel mesa-libGLU-devel qt5-qtdeclarative-devel"
                      "qt5-linguist tetgen-devel xerces-c-devel xkeyboard-config qt5-qtbase-devel"
        },
        'optional': {
            'ubuntu': "",
            'centos': ""
        },
    }