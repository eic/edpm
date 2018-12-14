import os
from distutils.dir_util import mkpath

from ejpm.engine.installation import PacketInstallationInstruction
from ejpm.engine.commands import run, env, workdir, is_not_empty_dir


class RootInstallation(PacketInstallationInstruction):
    """Provides data for building and installing root

    PackageInstallationContext is located in engine/installation.py

    """

    def __init__(self, version_tuple=(6, 14, 4)):
        """
        :param version: Root version
        """

        # Fill the common path pattern
        super(RootInstallation, self).__init__("root", version_tuple)

    def set_app_path(self, app_path):
        """Sets all variables like source dirs, build dirs, etc"""

        #
        # Root clone branch is like v6-14-04 so if a version is given by tuple (which is awaited at this point)
        # we format 'version' string so that we can use it as a branch name for clone command
        if self.version_tuple:
            self.version = 'v{}-{:02}-{:02}'.format(*self.version_tuple)  # v6-14-04

        #
        # use_common_dirs_scheme sets standard package variables:
        # version      = 'v{}-{:02}-{:02}'                 # Stringified version. Used to create directories and so on
        # source_path  = {app_path}/src/{version}          # Where the sources for the current version are located
        # build_path   = {app_path}/build/{version}        # Where sources are built. Kind of temporary dir
        # install_path = {app_path}/root-{version}         # Where the binary installation is
        self.use_common_dirs_scheme(app_path)

        #
        # Root download link. We will use github root mirror:
        # The tags have names like: v6-14-04
        # http://github.com/root-project/root.git
        # clone with shallow copy
        self.clone_command = "git clone --depth 1 -b {branch} https://github.com/root-project/root.git {source_path}" \
            .format(branch=self.version, source_path=self.source_path)

        #
        # ROOT packets to disable in our build (go with -D{name}=ON flag)
        self.disable = ["mysql", "alien", "asimag", "bonjour", "builtin_afterimage", "castor", "chirp", "dcache",
                        "fitsio", "gfal", "glite", "hdfs", "krb5", "odbc", "sapdb", "shadowpw", "srp", "xrootd"]

        #
        # ROOT packets to enable in our build (go with -D{name}=OFF flag)
        self.enable = ["roofit", "minuit2", "python"]

        # cmake command:
        # the  -Wno-dev  flag is to ignore the project developers cmake warnings for policy CMP0075
        self.build_cmd = "cmake -Wno-dev -DCMAKE_INSTALL_PREFIX={install_path} {enable} {disable} {source_path}" \
                         "&& cmake --build ." \
                         "&& cmake --build . --target install" \
            .format(enable=" ".join(["-D{}=ON".format(s) for s in self.enable]),  # enabled packets
                    disable=" ".join(["-D{}=OFF".format(s) for s in self.disable]),  # disabled packets
                    source_path=self.source_path,  # cmake source
                    install_path=self.install_path,  # Installation path
                    glb_make_options="-j8")  # make global options like '-j8'. Skip now

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

    fedora_required_packets = "git cmake gcc-c++ gcc binutils libX11-devel " \
                              "libXpm-devel libXft-devel libXext-devel"

    fedora_optional_packets = "gcc-gfortran openssl-devel pcre-devel " \
                              "mesa-libGL-devel mesa-libGLU-devel glew-devel ftgl-devel mysql-devel " \
                              "fftw-devel cfitsio-devel graphviz-devel " \
                              "avahi-compat-libdns_sd-devel libldap-dev python-devel " \
                              "libxml2-devel gsl-static"

    ubuntu_required_packets = "git dpkg-dev cmake g++ gcc binutils libx11-dev " \
                              "libxpm-dev libxft-dev libxext-dev"

    ubuntu_optional_packets = "gfortran libssl-dev libpcre3-dev " \
                              "xlibmesa-glu-dev libglew1.5-dev libftgl-dev " \
                              "libmysqlclient-dev libfftw3-dev libcfitsio-dev " \
                              "graphviz-dev libavahi-compat-libdnssd-dev " \
                              "libldap2-dev python-dev libxml2-dev libkrb5-dev " \
                              "libgsl0-dev libqt4-dev"