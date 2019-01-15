import inspect
import os
import sys

from ejpm.side_packages import provide_click_framework, provide_ansimarkup
from ejpm.engine.db import pass_db, PacketStateDatabase, IS_EJPM_OWNED, IS_SELECTED
from ejpm.engine.output import markup_print as mprint

# Try to import 'click' framework or to reference included version
provide_click_framework()   # Try to import 'click' framework or to reference included version
import click


def print_first_time_message():
    mprint("""
The database file doesn't exist. Probably you run 'ejpm' for one of the first times.
1. EJPM needs <b><blue>top-path</blue></b> from you to start. Run this command:

   > ejpm --top-path=<where-to-install-all>
   
2. Then you probably have CERN.ROOT installed (version >= 6.14.00). Run this:

   > ejpm add root `$ROOTSYS`
   
3. Then you can install all other packets (or add existing like #2):

   > ejpm install all
   
P.S. you can read this message by adding --help-first flag
     EJPM gitlab: https://gitlab.com/eic/ejpm
    """)
    click.echo()


_starting_workdir = ""


def _on_start():
    """Steps required in the beginning to run the app"""

    # add ansimarkup to python search path
    # ansimarkup allows to print console messages like <red>text</red>
    #add_ansimarkup_path()

    # Save the initial working directory
    # It is going to be restored in _on_close function
    global _starting_workdir
    _starting_workdir = os.getcwd()


def _on_close():
    """Finalizing function that is called after all commands"""

    # Restore the initial working directory if needed
    if _starting_workdir and _starting_workdir != os.getcwd():
        os.chdir(_starting_workdir)


def _print_packets_info(db):
    """Prints known installations of packets and what packet is selected"""

    assert (isinstance(db, PacketStateDatabase))

    mprint('\n<b><magenta>KNOWN PACKETS:</magenta></b> (*-active):')

    for packet_name in db.packet_names:
        mprint(' <b><blue>{}</blue></b>:'.format(packet_name))
        installs = db.get_installs(packet_name)
        for i, packet_path in enumerate(installs.keys()):
            install_data = installs[packet_path]
            is_owned_str = '<green>(owned)</green>' if install_data[IS_EJPM_OWNED] else ''
            is_active = install_data[IS_SELECTED]
            is_active_str = '*' if is_active else ' '
            path_str = packet_path
            id_str = "[{}]".format(i).rjust(4) if len(installs.keys()) > 1 else ""
            mprint("  {}{} {} {}".format(is_active_str, id_str, path_str, is_owned_str))



@click.group(invoke_without_command=True)
@click.option('--debug/--no-debug', default=False)
@click.option('--top-dir', default="")
@pass_db
@click.pass_context
def ejpm_cli(ctx, db, debug, top_dir):
    """EJPM stands for
    """

    # Run initialization stuff
    _on_start()

    # Add _on_close function that will restore working directory
    ctx.call_on_close(_on_close)

    #
    # Now the database...
    assert(isinstance(db, PacketStateDatabase))

    # by default, db file should be at the same place as ejpm.py. Parent of dir of this file
    db_file_dir = os.path.dirname(os.path.dirname(inspect.stack()[0][1]))
    db.file_path = os.path.join(db_file_dir, "db.json")

    # did user asks us to set the top dir
    if top_dir:
        db.top_dir = top_dir
        db.save()

    # check if DB file already exists
    if not db.exists():
        print_first_time_message()
        exit(0)

    # load  the database state
    db.load()

    if ctx.invoked_subcommand is None:

        mprint("<b><blue>ejpm</blue></b> v.{}.{}.{}".format(*(0, 0, 1)))
        mprint("<b><blue>top dir:</blue></b> {top_dir}".format(top_dir=db.top_dir))
        _print_packets_info(db)

        # click.echo('I was invoked without subcommand')
    else:
        pass
        # click.echo('I am about to invoke %s' % ctx.invoked_subcommand)

    #click.echo('Debug mode is %s' % ('on' if debug else 'off'))


from ejpm.cli.env import env as env_group
from ejpm.cli.install import install as install_group
from ejpm.cli.find import find as find_group

ejpm_cli.add_command(install_group)
ejpm_cli.add_command(find_group)
ejpm_cli.add_command(env_group)

if __name__ == '__main__':
    ejpm_cli()
