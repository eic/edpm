import os
from distutils.dir_util import mkpath

from ejpm.engine.env_gen import Set, Prepend
from ejpm.side_packages import provide_click_framework

provide_click_framework()
import click

from ejpm.engine.installation import PacketInstallationInstruction
from ejpm.engine.commands import run, env, workdir, is_not_empty_dir


class RaveInstallation(PacketInstallationInstruction):
    """Provides data for building and installing root

    PackageInstallationContext is located in installation.py and contains the next standard package variables:
    """

    def __init__(self, version_tuple=(0, 6, 25)):
        # Call parent constructor to fill version, app_path ... and others
        # (!) it is called AFTER we override self.version
        super(RaveInstallation, self).__init__('rave', version_tuple)

    def set_app_path(self, app_path):
        """Sets all variables like source dirs, build dirs, etc"""
        #
        # use_common_dirs_scheme sets standard package variables:
        # version      = 'v{}-{:02}-{:02}'                 # Stringified version. Used to create directories and so on
        # source_path  = {app_path}/src/{version}          # Where the sources for the current version are located
        # build_path   = {app_path}/build/{version}        # Where sources are built. Kind of temporary dir
        # install_path = {app_path}/root-{version}         # Where the binary installation is
        self.use_common_dirs_scheme(app_path)

        # ENV RAVEPATH $INSTALL_DIR_RAVE

        # version used in a link and in the archive
        # both download link and the archive use a name like rave-0.6.25
        link_version = "rave-{}.{}.{}".format(*self.version_tuple)

        #
        # The link to download RAVE. It is like:
        # https://rave.hepforge.org/downloads?f=rave-0.6.25.tar.gz
        self.download_link = "https://rave.hepforge.org/downloads?f={link_version}.tar.gz" \
            .format(link_version=link_version)

        #
        # Command to download and exctract RAVE
        self.download_command = "wget -N -O {version}.tar.gz --no-check-certificate {download_link}" \
                                "&& rm -rf {version}" \
                                "&& tar -xzf {version}.tar.gz" \
                                "&& mv {link_version} {version}" \
            .format(version=self.version,
                    link_version=link_version,
                    download_link=self.download_link)

        # Support for including RAVE in the build of GenFit is completely broken.
        # Neither the pkgconfig nor RAVE_XXX envars method actually works. Also,
        # rave seems to install with a bunch of "RaveDllExport" keywords in the
        # headers which so be defined as empty strings for Linux. The only file
        # that defines them is vcconfig.h which exists only in the build directory
        # and not in the installed include directory. VERY frustrating! The solution
        # requires stripping this out of the RAVE headers since the ultra-crappy
        # GenFit CMake system does not honor even the CXXFLAGS passed into it!

        self.build_command = "./configure --disable-java --prefix=$RAVEPATH " \
                             '&& CXXFLAGS="-std=c++11" make -j{glb_make_options} install' \
                             "&& for f in $(ls $RAVEPATH/include/rave/*.h); do sed -i 's/RaveDllExport//g' $f; done" \
            .format(install_path=self.install_path, glb_make_options="", version=self.version)

    def step_install(self):
        self.step_download()
        self.step_build()

    def step_download(self):
        """Downloads and extracts RAVE"""

        # Check the directory exists and not empty
        if is_not_empty_dir(self.source_path):
            return  # The directory exists and is not empty. Assume it cloned

        mkpath(self.download_path)     # Create source directory and any missing ancestor directories if not there
        workdir(self.download_path)    # Go to 'src' dir
        run(self.download_command)     # Download and extract

    def step_build(self):
        # Create build directory

        # If we or user installed CLHEP it should be in environ
        if 'CLHEPPATH' not in os.environ:
            # Ubuntu and other systems may have CLHEP installed through official repos
            env('CLHEP_INCLUDE_DIR', '/usr/include')  # or /usr/include/CLHEP/
            env('CLHEP_LIB_DIR', '/usr/lib')

        env('RAVEPATH', self.install_path)

        # Rave uses ./configure so we building it in {source_path}
        # go to our build directory
        workdir(self.source_path)

        # run cmake && make && install
        run(self.build_command)

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
