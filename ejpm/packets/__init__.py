import importlib
import pkgutil

import ejpm
from ejpm.engine.installation import PacketInstallationInstruction

from ejpm.side_packages import provide_click_framework

# Try to import 'click' framework or to reference included version
provide_click_framework()  # Try to import 'click' framework or to reference included version
import click


def import_all_submodules():
    for (module_loader, name, ispkg) in pkgutil.iter_modules([ejpm.packets.__path__[0]]):
        importlib.import_module('.' + name, __package__)


class PacketManager:

    def __init__(self):
        # We need to import submodules at least once to get __submodules__() function work later
        import_all_submodules()

        # But now we just import and create them manually
        self.packets = {}
        self.env_generators = {}

        # Create all subclasses of PacketInstallationInstruction and add here
        for cls in PacketInstallationInstruction.__subclasses__():
            installer = cls()
            self.add_installer(installer)

            if hasattr(installer, 'gen_env'):
                self.add_env_generator(installer.name, installer.gen_env)

    def add_installer(self, installer):
        self.packets[installer.name] = installer

    def add_env_generator(self, name, env_gen):
        self.env_generators[name] = env_gen

    def gen_bash_environment(self, name_paths):

        output = ""     # a string holding the result

        # Go through provided name-path pairs:
        for name, path in name_paths.items():

            # If we have a generator for this program
            if name in self.env_generators.keys():
                output += "# =============================\n# {}\n# =============================\n".format(name)
                env_gen = self.env_generators[name]
                steps_list = []

                for step in env_gen(path):
                    output += step.gen_bash(steps_list)
                    steps_list.append(step)
        return output


# Create a PacketManager class and @pass_pm decorator so our commands could use it
pass_pm = click.make_pass_decorator(PacketManager, ensure=True)


