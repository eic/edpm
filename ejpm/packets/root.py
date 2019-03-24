"""
This file provides information of how to build and configure CERN.ROOT:
https://github.com/root-project/root

"""

import os
from distutils.dir_util import mkpath

from ejpm.engine import env_gen
from ejpm.engine.installation import PacketInstallationInstruction
from ejpm.engine.commands import run, env, workdir, is_not_empty_dir


ROOTSYS = "ROOTSYS"


class RootInstallation(PacketInstallationInstruction):
    """Provides data for building and installing root

    PackageInstallationContext is located in engine/installation.py

    """

    class DefaultConfigFields(object):
        pass


    def __init__(self, build_threads=8):
        """
        :param version: Root version
        """

        # Fill the common path pattern
        super(RootInstallation, self).__init__("root")
        self.build_threads = build_threads


    def setup(self, app_path):
        """Sets all variables like source dirs, build dirs, etc"""

        #
        # Root clone branch is like v6-14-04 so if a version is given by tuple (which is awaited at this point)
        # we format 'version' string so that we can use it as a branch name for clone command
        version = 'v{}-{:02}-{:02}'.format(6, 16, 0)  # v6-14-04

        #
        # use_common_dirs_scheme sets standard package variables:
        # version      = 'v{}-{:02}-{:02}'                 # Stringified version. Used to create directories and so on
        # source_path  = {app_path}/src/{version}          # Where the sources for the current version are located
        # build_path   = {app_path}/build/{version}        # Where sources are built. Kind of temporary dir
        # install_path = {app_path}/root-{version}         # Where the binary installation is
        self.use_common_dirs_scheme(app_path, version)

        #
        # Root download link. We will use github root mirror:
        # The tags have names like: v6-14-04
        # http://github.com/root-project/root.git
        # clone with shallow copy
        self.clone_command = "git clone --depth 1 -b {branch} https://github.com/root-project/root.git {source_path}" \
            .format(branch=version, source_path=self.source_path)

        #
        # ROOT packets to disable in our build (go with -D{name}=ON flag)
        # the  -Wno-dev  flag is to ignore the project developers cmake warnings for policy CMP0075
        self.build_cmd = "cmake -Wno-dev -DCMAKE_INSTALL_PREFIX={install_path} " \
                         " -Dgdml=ON" \
		                 " -Dminuit2=ON" \
                         " {source_path}" \
                         "&& cmake --build . -- -j {build_threads}" \
                         "&& cmake --build . --target install" \
            .format(source_path=self.source_path,       # cmake source
                    install_path=self.install_path,     # Installation path
                    build_threads=self.build_threads)   # make global options like '-j8'. Skip now

    def step_install(self):
        self.step_clone_root()
        self.step_build_root()

    def step_clone_root(self):
        """Clones root from github mirror"""

        # Check the directory exists and not empty
        if is_not_empty_dir(self.source_path):
            return                                      # The directory exists and is not empty. Assume it cloned

        mkpath(self.source_path)     # Create the directory and any missing ancestor directories if not there
        run(self.clone_command)      # Execute git clone command

    def step_build_root(self):
        """Builds root from the ground"""

        # Create build directory
        run('mkdir -p {}'.format(self.build_path))

        env('ROOTSYS', self.install_path)

        # go to our build directory
        workdir(self.build_path)

        # run cmake && make && install
        run(self.build_cmd)

    def step_rebuild_root(self):
        """Clear root build directory"""

        # clear sources directories if needed
        run('rm -rf {}'.format(self.source_path))
        run('rm -rf {}'.format(self.build_path))

        # Now run build root
        self.step_build_root()

    @staticmethod
    def gen_env(data):
        install_path = data['install_path']

        def update_python_environment():
            """Function that will update ROOT environment in python
            We need this function because we DON'T want source thisroot in python
            """

            root_bin = os.path.join(install_path, 'bin')
            root_lib = os.path.join(install_path, 'lib')
            root_jup = os.path.join(install_path, 'etc','notebook')

            env_updates = [
                env_gen.Set('ROOTSYS', install_path),
                env_gen.Prepend('PATH', root_bin),
                env_gen.Prepend('LD_LIBRARY_PATH', root_lib),
                env_gen.Prepend('DYLD_LIBRARY_PATH', root_lib),
                env_gen.Prepend('PYTHONPATH', root_lib),
                env_gen.Prepend('CMAKE_PREFIX_PATH', install_path),
                env_gen.Prepend('JUPYTER_PATH', root_jup),
            ]

            for updater in env_updates:
                updater.update_python_env()

        # We just call thisroot.xx in different shells

        raw = env_gen.RawText(
            "source {}".format(os.path.join(install_path, 'bin', 'thisroot.sh')),
            "source {}".format(os.path.join(install_path, 'bin', 'thisroot.csh')),
            update_python_environment
        )

        yield raw

    #
    # OS dependencies are a map of software packets installed by os maintainers
    # The map should be in form:
    # os_dependencies = { 'required': {'ubuntu': "space separated packet names", 'fedora': "..."},
    #                     'optional': {'ubuntu': "space separated packet names", 'fedora': "..."}
    #                   }
    os_dependencies = {
        'required': {
            'ubuntu': "git dpkg-dev cmake g++ gcc binutils libx11-dev libxpm-dev libxft-dev libxext-dev",
            'fedora': "git cmake gcc-c++ gcc binutils libX11-devel libXpm-devel libXft-devel libXext-devel"
        },
        'optional': {
            'ubuntu': "gfortran libssl-dev libpcre3-dev "
                      "xlibmesa-glu-dev libglew1.5-dev libftgl-dev "
                      "libmysqlclient-dev libfftw3-dev libcfitsio-dev "
                      "graphviz-dev libavahi-compat-libdnssd-dev "
                      "libldap2-dev python-dev libxml2-dev libkrb5-dev "
                      "libgsl0-dev libqt4-dev",

            'fedora': "gcc-gfortran openssl-devel pcre-devel "
                      "mesa-libGL-devel mesa-libGLU-devel glew-devel ftgl-devel mysql-devel "
                      "fftw-devel cfitsio-devel graphviz-devel "
                      "avahi-compat-libdns_sd-devel libldap-dev python-devel "
                      "libxml2-devel gsl-static"
        },
    }



def root_find():
    """Looks for CERN ROOT package
    :return [str] - empty list if not found or a list with 1 element - ROOTSYS path

    The only way to find ROOT is by checking for ROOTSYS package,
    The function family xxx_find() return list in general
    so this function returns ether empty list or a list with 1 element - root path
    """

    # The only way to find a CERN ROOT is by
    result = []

    # Check ROOTSYS environment variable
    if ROOTSYS not in os.environ:
        print("<red>ROOTSYS</red> not found in the environment")
        return result

    # Now check ROOTSYS exists in the system
    root_sys_path = os.environ[ROOTSYS]
    if not os.path.isdir(root_sys_path):
        print("WARNING", " ROOTSYS points to nonexistent directory of a file")
        return result

    # Looks like root exists, return the path
    return [root_sys_path]
