import os
import click

from ejpm.cli.ejpm_context import pass_ejpm_context, DB_FILE_PATH
from ejpm.engine.db import PacketStateDatabase
from ejpm.engine.output import markup_print as mprint


def print_first_time_message():
    mprint("""
The database file doesn't exist. Probably you run 'ejpm' for one of the first times.

1. Set <b><blue>top-dir</blue></b> to start. This is where all missing packets will be installed.   

   > ejpm --top-dir=<where-to-install-all>
   
2. You may have CERN.ROOT installed (req. version >= 6.14.00). Run this:

   > ejpm add root `$ROOTSYS`
   
3. Then you can install all other packets (or add existing like #2):

   > ejpm install missing
   

P.S - you can read this message by adding --help-first flag
    - EJPM gitlab: https://gitlab.com/eic/ejpm
    - This message will disappear after running any command that make changes
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

    from ejpm.engine.db import IS_OWNED, IS_ACTIVE, INSTALL_PATH
    assert (isinstance(db, PacketStateDatabase))

    mprint('\n<b><magenta>KNOWN PACKETS:</magenta></b> (*-active):')

    for packet_name in db.packet_names:
        mprint(' <b><blue>{}</blue></b>:'.format(packet_name))
        installs = db.get_installs(packet_name)
        for i, installation in enumerate(installs):
            is_owned_str = '<green>(owned)</green>' if installation[IS_OWNED] else ''
            is_active = installation[IS_ACTIVE]
            is_active_str = '*' if is_active else ' '
            path_str = installation[INSTALL_PATH]
            id_str = "[{}]".format(i).rjust(4) if len(installs) > 1 else ""
            mprint("  {}{} {} {}".format(is_active_str, id_str, path_str, is_owned_str))



@click.group(invoke_without_command=True)
@click.option('--debug/--no-debug', default=False)
@click.option('--top-dir', default="")
@pass_ejpm_context
@click.pass_context
def ejpm_cli(ctx, ectx, debug, top_dir):
    """EJPM stands for
    """

    # Run on-start and set on-close routines
    _on_start()                     # Run initialization stuff
    ctx.call_on_close(_on_close)    # Add _on_close function that will restore working directory

    # Package state database
    db = ectx.db

    # user asks to set the top dir
    if top_dir:
        db.top_dir = top_dir
        db.save()

    # check if DB file already exists
    if not db.exists():
        print_first_time_message()
    else:
        # load the database state
        db.load()

        # if there is no commands and we loaded the DB lets print some info:
        if ctx.invoked_subcommand is None:
            from ejpm.__version__ import __version__
            mprint("<b><blue>EJPM</blue></b> v{}".format(__version__))
            mprint("<b><blue>top dir :</blue></b>\n  {}".format(db.top_dir))
            mprint("<b><blue>state db:</blue></b> (users are encouraged to inspect/edit it)\n  {}"
                   .format(ectx.config[DB_FILE_PATH]))
            _print_packets_info(db)


from ejpm.cli.env import env as env_group
from ejpm.cli.install import install as install_group
from ejpm.cli.find import find as find_group

ejpm_cli.add_command(install_group)
ejpm_cli.add_command(find_group)
ejpm_cli.add_command(env_group)

if __name__ == '__main__':
    ejpm_cli()
