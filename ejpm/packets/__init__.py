import importlib
import pkgutil
import ejpm.packets.root_install
from ejpm.engine.installation import PacketInstallationInstruction
from ejpm.packets.root_install import RootInstallationInstruction
from ejpm.engine.db import PacketStateDatabase


def print_classes():
    def get_steps(cls):
        return [i for i in cls.__dict__.keys() if i.startswith('step_')]

    for (module_loader, name, ispkg) in pkgutil.iter_modules([ejpm.packets.__path__[0]]):
        importlib.import_module('.' + name, __package__)

    #all_my_base_classes = {cls.__name__: cls for cls in PackageInstallationContext.__subclasses__()}
    for cls in PacketInstallationInstruction.__subclasses__():
        print(cls.name)
        print(get_steps(cls))
    #print(all_my_base_classes)


class PacketManager:
    def __init__(self, db):
        print_classes()
        assert isinstance(db, PacketStateDatabase)
        self._installers["root"] = RootInstallationInstruction(db.top_dir)




