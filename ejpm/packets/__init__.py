import importlib
import io
import pkgutil

import ejpm
from ejpm.engine.installation import PacketInstallationInstruction


def import_all_submodules():
    for (module_loader, name, ispkg) in pkgutil.iter_modules([ejpm.packets.__path__[0]]):
        importlib.import_module('.' + name, __package__)

class PacketManager(object):

    def __init__(self):
        # We need to import submodules at least once to get __submodules__() function work later
        import_all_submodules()

        # But now we just import and create them manually
        self.installers_by_name = {}
        self.installers_by_tags = {}
        self.env_generators = {}

        # The next are collection of requirements for different operating systems
        # The type is map to have requirements by packets, i.e.:
        #     self.fedora_required_packets['ejana'] - list for ejana
        self.os_deps_by_name = {}

        # Create all subclasses of PacketInstallationInstruction and add here
        for cls in PacketInstallationInstruction.__subclasses__():
            installer = cls()
            self.add_installer(installer)
            self.add_env_generator(installer)
            self.add_os_deps(installer)

    def add_os_deps(self, installer):
        """Adds os dependencies to global os_dependencies_by_name map"""

        # First, we add default structure with empty deps
        result = {'required': {'ubuntu': "", 'fedora': ""},
                  'optional': {'ubuntu': "", 'fedora': ""}}

        # Then we check if installer defines its dependencies
        if hasattr(installer, 'os_dependencies'):
            result.update(installer.os_dependencies)

        # Set the result by installer name
        self.os_deps_by_name[installer.name] = result

    def add_installer(self, installer):
        self.installers_by_name[installer.name] = installer

        # default tag is installer name itself
        self.installers_by_tags[installer.name] = ('', installer)
        if hasattr(installer, 'tags'):
            # installer has tags
            # get name of the default tag
            default_tag = installer.default_tag if hasattr(installer, 'default_tag') else ''
            tag_names = [name for name in installer.tags.keys() if name != default_tag]

            for tag_name in tag_names:
                # 'full name' is <app name>-<tag name>
                tag_full_name = "{}-{}".format(installer.name, tag_name)
                self.installers_by_tags[tag_full_name] = (tag_name, installer)

    def add_env_generator(self, installer):
        """Adds installer environment generator to env_generators map"""

        if hasattr(installer, 'gen_env'):
            self.env_generators[installer.name] = installer.gen_env

    def get_installation_names(self, installer_name):
        """
        Returns name of the package + dependencies ejpm can install
        so it is like: ['CLHEP', 'root', ..., 'ejana'] for installer_name=ejana
        it is single: ['CLHEP'] for installer_name='CLHEP'

        :param installer_name: name of packet like 'ejana'
        :return: list with dependencies names and installer name itself
        """

        deps = self.installers_by_name[installer_name].required_deps

        # If we install just a single packet desired_names a single name
        return deps + [installer_name] if deps else [installer_name]

    def gen_shell_env_text(self, name_data, shell='bash'):
        """Generates a text that sets environment for a given shell """

        output = ""     # a string holding the result

        # Go through provided name-path pairs:
        for name, data in name_data.items():

            # if some packet has no data, or there is no environ generator for it, we skip it
            if not data or name not in self.env_generators.keys():
                continue

            env_gen = self.env_generators[name]

            output += "\n"
            output += "# =============================\n"
            output += "# {}\n".format(name)
            output += "# =============================\n"

            # env_gen(data) provides environment manipulation instructions based on the given data
            for step in env_gen(data):
                output += step.gen_csh() if shell == 'csh' else step.gen_bash() # bash or csh?
                output += '\n'
        return output

    def gen_bash_env_text(self, name_data):
        """Generates a text that sets environment for bash shell """
        return self.gen_shell_env_text(name_data, shell='bash')

    def gen_csh_env_text(self, name_data):
        """Generates a text that sets environment for csh/tcsh shell """
        return self.gen_shell_env_text(name_data, shell='csh')

    def update_python_env(self, name_data):
        """Updates python environment according to (name,paths) pairs
        :param name_paths:
        """

        # Go through provided name-path pairs:
        for name, data in name_data.items():

            # If we have a generator for this program and installation data
            if data and name in self.env_generators.keys():
                env_gens = self.env_generators[name]
                for env_gen in env_gens(data):          # Go through 'environment generators' look engine/env_gen.py
                    env_gen.update_python_env()         # Do environment update




