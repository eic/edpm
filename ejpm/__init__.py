import os
import click

from ejpm.cli.ejpm_context import pass_ejpm_context, DB_FILE_PATH, ENV_CSH_PATH, ENV_SH_PATH
from ejpm.engine.db import PacketStateDatabase
from ejpm.engine.output import markup_print as mprint


def print_first_time_message():
    mprint("""
The database file doesn't exist. Probably you run 'ejpm' for one of the first times.

1. Install or check OS maintained required packages:
    > ejpm req ubuntu         # for all packets ejpm knows to built/install
    > ejpm req usubnu ejana   # for ejana and its dependencies only
   
   * - at this point put 'ubuntu' for debian and 'fedora' for RHEL and CentOS systems. 
   Will be updated in future to support macOS, and to have grained versions

1. Set <b><blue>top-dir</blue></b> to start. This is where all missing packets will be installed.   

   > ejpm --top-dir=<where-to-install-all>
   
2. You may have CERN.ROOT installed (req. version >= 6.14.00). Run this:

   > ejpm set root `$ROOTSYS`
   
   You may set paths for other installed dependencies:
   > ejpm install ejana --missing --explain    # to see missing dependencies
   > ejpm set <name> <path>                    # to set dependency path
   
3. Then you can install all missing dependencies:

   > ejpm install ejana --missing
   

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
    """EJPM stands for EIC Jana Packet Manager
    """

    # Run on-start and set on-close routines
    _on_start()                     # Run initialization stuff
    ctx.call_on_close(_on_close)    # Add _on_close function that will restore working directory

    # Package state database
    db = ectx.db
    assert isinstance(db, PacketStateDatabase)

    ectx.load_db_if_exists()

    # user asks to set the top dir
    if top_dir:
        db.top_dir = os.path.abspath(os.path.normpath(top_dir))
        db.save()

    # check if DB file already exists
    if not db.exists():
        print_first_time_message()
        ectx.construct_packet_manager()
    else:
        # load the database state
        db.load()
        ectx.construct_packet_manager()

        # At this point we already know what packets we know how to build/install
        db.known_packet_names = ectx.pm.installers_by_name.keys()



        # if there is no commands and we loaded the DB lets print some info:
        if ctx.invoked_subcommand is None:
            from ejpm.version import version
            mprint("<b><blue>EJPM</blue></b> v{}".format(version))
            mprint("<b><blue>top dir :</blue></b>\n  {}", db.top_dir)
            mprint("<b><blue>state db :</blue></b>\n  {}", ectx.config[DB_FILE_PATH])
            mprint("  (users are encouraged to inspect/edit it)")
            mprint("<b><blue>env files :</blue></b>\n  {}\n  {}", ectx.config[ENV_SH_PATH], ectx.config[ENV_CSH_PATH])
            _print_packets_info(db)


from ejpm.cli.env import env as env_group
from ejpm.cli.install import install as install_group
from ejpm.cli.find import find as find_group
from ejpm.cli.req import req as requirements_command
from ejpm.cli.set import set as set_command
from ejpm.cli.rm import rm as rm_command

ejpm_cli.add_command(install_group)
ejpm_cli.add_command(find_group)
ejpm_cli.add_command(env_group)
ejpm_cli.add_command(requirements_command)
ejpm_cli.add_command(set_command)
ejpm_cli.add_command(rm_command)

if __name__ == '__main__':
    ejpm_cli()
