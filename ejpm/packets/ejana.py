"""
This file provides information of how to build and configure EIC Jana (ejana) framework:
https://gitlab.com/eic/ejana

"""

import os

from ejpm.engine.env_gen import Set, Prepend
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


    def __init__(self, build_threads=8):
        """

        :param default_tag: Root version
        """


        super(EjanaInstallation, self).__init__('ejana')
        self.build_threads = build_threads
        self.clone_command = ""
        self.build_command = ""
        self.required_deps = ['clhep', 'root', 'rave', 'genfit', 'hepmc', 'eic-smear', 'jana']


    def _setup_dev(self, app_path):
        """Sets all variables like source dirs, build dirs, etc"""

        # For dev version we don't use common path scheme
        self.config['app_path'] = app_path

        branch = 'master'
        # The directory with source files for current version
        self.config['source_path'] = "{app_path}/dev".format(app_path=self.app_path)
        self.config['build_path'] = "{app_path}/dev/.build".format(app_path=self.app_path)  # build in dev directory
        self.config['install_path'] = "{app_path}/dev/build".format(app_path=self.app_path)

        #
        # ejana download link
        self.clone_command = "git clone -b {branch} https://gitlab.com/eic/ejana.git {source_path}"\
            .format(branch=branch, source_path=self.source_path)

        # cmake command:
        # the  -Wno-dev  flag is to ignore the project developers cmake warnings for policy CMP0075
        self.build_cmd = "cmake -Wno-dev -DCMAKE_INSTALL_PREFIX={install_path} {source_path}" \
                         "&& cmake --build . -- -j {build_threads}" \
                         "&& cmake --build . --target install" \
            .format(source_path=self.source_path,  # cmake source
                    install_path=self.install_path,  # Installation path
                    build_threads=self.build_threads)  # make global options like '-j8'. Skip now

    def setup(self, app_path):
        """Sets all variables like source dirs, build dirs, etc"""

        #if self.selected_tag == 'dev':

        # (!) at this point we alwais use dev environment
        return self._setup_dev(app_path)

        # it is not a dev setup
        branch = 'master'

        #
        # use_common_dirs_scheme sets standard package variables:
        # version      = 'v{}-{:02}-{:02}'                 # Stringified version. Used to create directories and so on
        # source_path  = {app_path}/src/{version}          # Where the sources for the current version are located
        # build_path   = {app_path}/build/{version}        # Where sources are built. Kind of temporary dir
        # install_path = {app_path}/root-{version}         # Where the binary installation is
        self.use_common_dirs_scheme(app_path, branch)

        #
        # JANA download link. Clone with shallow copy
        # TODO accept version tuple to get exact branch
        self.clone_command = "git clone --depth 1 -b {branch} https://gitlab.com/eic/ejana.git {source_path}"\
            .format(branch=self.selected_tag, source_path=self.source_path)

        # cmake command:
        # the  -Wno-dev  flag is to ignore the project developers cmake warnings for policy CMP0075
        self.build_cmd = "cmake -Wno-dev -DCMAKE_INSTALL_PREFIX={install_path} {source_path}" \
                         "&& cmake --build . -- -j {build_threads}" \
                         "&& cmake --build . --target install" \
                         .format(source_path=self.source_path,      # cmake source
                                 install_path=self.install_path,    # Installation path
                                 build_threads=self.build_threads)  # make global options like '-j8'. Skip now

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
        path = data['install_path']
        """Generates environments to be set"""

        yield Prepend('JANA_PLUGIN_PATH', os.path.join(path, 'plugins'))
        yield Prepend('PATH', os.path.join(path, 'bin'))

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
