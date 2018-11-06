import os
import utilites
from collections import OrderedDict

utilites.provide_click_framework()
import click

from context import Context, PackageInstallationContext, run, env, workdir, execute_current_plan


class RootInstallationContext(PackageInstallationContext):
    """Provides data for building and installing root

    PackageInstallationContext is located in context.py and contains the next standard package variables:

    version      = 'v{}-{:02}-{:02}'                    # Stringified version. Used to create directories and so on
    glb_app_path = Context.work_dir                     # The directory where all other packages are installed
    app_path     = {glb_app_path}/{name}                # This package directory for source/build/bin
    source_path  = {app_path}/src/{version}             # Where the sources for the current version are located
    build_path   = {app_path}/build/{version}           # Where sources are built. Kind of temporary dir
    install_path = {app_path}/bin/{abi_name}            # Where the binary installation is

    """

    def __init__(self, version_tuple=(6, 14, 4)):

        # Fill the common path pattern
        super(RootInstallationContext, self).__init__("root", version_tuple)

        #
        # Root clone branch is like v6-14-04 so we format binary version accordingly
        branch = 'v{}-{:02}-{:02}'.format(*version_tuple)     # v6-14-04

        #
        # Root download link. We will use github root mirror:
        # The tags have names like: v6-14-04
        # http://github.com/root-project/root.git
        # clone with shallow copy
        self.clone_command = "git clone --depth 1 -b {branch} https://github.com/root-project/root.git {version}"\
            .format(branch=branch, version=self.version)

        #
        # ROOT packages to disable in our build (go with -D{name}=ON flag)
        self.disable = ["mysql", "alien", "asimag", "bonjour", "builtin_afterimage", "castor", "chirp", "dcache",
                   "fitsio", "gfal", "glite", "hdfs", "krb5", "odbc", "sapdb", "shadowpw", "srp"]

        #
        # ROOT packages to enable in our build (go with -D{name}=OFF flag)
        self.enable = ["roofit", "minuit2", "python", "builtin_xrootd"]

        # mcake command:
        # the  -Wno-dev  flag is to ignore the project developers cmake warnings for policy CMP0075
        self.build_cmd = "cmake -Wno -dev -DCMAKE_INSTALL_PREFIX={install_path} {enable} {disable} {source_path}" \
                         "&& cmake --build ." \
                         "&& cmake --build . --target install"\
            .format(enable=" ".join(["-D{}=ON".format(s) for s in self.enable]),       # enabled packages
                    disable=" ".join(["-D{}=OFF".format(s) for s in self.disable]),    # disabled packages
                    source_path=self.source_path,                            # cmake source
                    install_path=self.install_path,                          # Installation path
                    glb_make_options="-j8")                                  # make global options like '-j8'. Skip now

        self.fedora_required_packages = "git cmake gcc-c++ gcc binutils libX11-devel libXpm-devel libXft-devel libXext-devel"

        self.fedora_optional_packages = (" gcc-gfortran openssl-devel pcre-devel "
                                         "mesa-libGL-devel mesa-libGLU-devel glew-devel ftgl-devel mysql-devel "
                                         "fftw-devel cfitsio-devel graphviz-devel "
                                         "avahi-compat-libdns_sd-devel libldap-dev python-devel "
                                         "libxml2-devel gsl-static")



        self.ubuntu_required_packages = "git dpkg-dev cmake g++ gcc binutils libx11-dev libxpm-dev libxft-dev libxext-dev"

        self.ubuntu_optional_packages = (" gfortran libssl-dev libpcre3-dev "
                                         "xlibmesa-glu-dev libglew1.5-dev libftgl-dev "
                                         "libmysqlclient-dev libfftw3-dev libcfitsio-dev "
                                         "graphviz-dev libavahi-compat-libdnssd-dev "
                                         "libldap2-dev python-dev libxml2-dev libkrb5-dev "
                                         "libgsl0-dev libqt4-dev")


    def install(self):
        self.step_clone_root()

    def step_get_sources(self):
        pass

    def step_clone_root(self):

        # Create directories if needed
        run('mkdir -p {}'.format(self.source_path))

        # Go to 'src' dir (which is a parent of self.source_path)
        download_path = os.path.abspath(os.path.join(self.source_path, os.pardir))
        workdir(download_path)

        # Execute git clone command
        run(self.clone_command)

    def step_build_root(self, rebuild=False):
        # Create build directory
        run('mkdir -p {}'.format(self.build_path))

        env('ROOTSYS', self.install_path)

        # go to our build directory
        workdir(self.build_path)


        # run cmake && make && install
        run(self.build_cmd)






