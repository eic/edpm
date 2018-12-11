import os
import re

from ejpm.engine.output import color_echo
import ejpm.engine.db

ROOTSYS = 'ROOTSYS'

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
        color_echo("ROOTSYS", " not found in the environment", 'red')
        return result

    # Now check ROOTSYS exists in the system
    root_sys_path = os.environ[ROOTSYS]
    if not os.path.isdir(root_sys_path):
        color_echo("WARNING", " ROOTSYS points to nonexistent directory of a file")
        return result

    # Looks like root exists, return the path
    return [root_sys_path]



