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

        # Create all subclasses of PacketInstallationInstruction and add here
        for cls in PacketInstallationInstruction.__subclasses__():
            self.add_installer(cls())

    def add_installer(self, installer):
        self.packets[installer.name] = installer


# Create a PacketManager class and @pass_pm decorator so our commands could use it
pass_pm = click.make_pass_decorator(PacketManager, ensure=True)


