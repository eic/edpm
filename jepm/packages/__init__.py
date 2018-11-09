import inspect
import sys
import jepm.packages.root

def print_classes():
    clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    print(clsmembers)