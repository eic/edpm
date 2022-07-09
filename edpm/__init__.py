import os
import click

from edpm.engine.api import pass_edpm_context, DB_FILE_PATH, ENV_CSH_PATH, ENV_SH_PATH, edpmApi, print_packets_info
from edpm.engine.db import PacketStateDatabase
from edpm.engine.output import markup_print as mprint


def print_first_time_message():
    mprint("""
The database file doesn't exist. Probably you run 'edpm' for one of the first times.

1. Install or check OS maintained required packages:
    > edpm req ubuntu         # for all packets edpm knows to built/install
    > edpm req ubuntu ejana   # for ejana and its dependencies only
   
   * - at this point put 'ubuntu' for debian and 'centos' for RHEL and CentOS systems. 
   Will be updated in future to support macOS, and to have grained versions

1. Set <b><blue>top-dir</blue></b> to start. This is where all missing packets will be installed.   

   > edpm --top-dir=<where-to-install-all>
   
2. You may have CERN.ROOT installed (req. version >= 6.14.00). Run this:

   > edpm set root `$ROOTSYS`
   
   You may set paths for other installed dependencies:
   > edpm install ejana --missing --explain    # to see missing dependencies
   > edpm set <name> <path>                    # to set dependency path
   
3. Then you can install all missing dependencies:

   > edpm install ejana --missing
   

P.S - you can read this message by adding --help-first flag
    - edpm gitlab: https://gitlab.com/eic/edpm
    - This message will disappear after running any command that make changes
    """)
    click.echo()


_starting_workdir = ""

@click.group(invoke_without_command=True)
@click.option('--debug/--no-debug', default=False)
@click.option('--top-dir', default="")
@pass_edpm_context
@click.pass_context
def edpm_cli(ctx, ectx, debug, top_dir):
    """edpm stands for EIC Jana Packet Manager"""

    assert isinstance(ectx, edpmApi)    # Type check for ectx

    # Load db and modules from disk
    db_existed = ectx.load_shmoad_ugly_toad()    # False => Couldn't load and used default

    # user asks to set the top dir
    if top_dir:
        ectx.db.top_dir = os.path.abspath(os.path.normpath(top_dir))
        ectx.db.save()
        db_existed = True

    # check if DB file already exists
    if not db_existed:
        print_first_time_message()
    else:
        # if there is no commands and we loaded the DB lets print some info:
        if ctx.invoked_subcommand is None:
            from edpm.version import version
            mprint("<b><blue>edpm</blue></b> v{}".format(version))
            mprint("<b><blue>top dir :</blue></b>\n  {}", ectx.db.top_dir)
            mprint("<b><blue>state db :</blue></b>\n  {}", ectx.config[DB_FILE_PATH])
            mprint("  (users are encouraged to inspect/edit it)")
            mprint("<b><blue>env files :</blue></b>\n  {}\n  {}", ectx.config[ENV_SH_PATH], ectx.config[ENV_CSH_PATH])
            print_packets_info(ectx.db)

from edpm.cli.env import env as env_group
from edpm.cli.install import install as install_group
from edpm.cli.find import find as find_group
from edpm.cli.req import req as requirements_command
from edpm.cli.set import set as set_command
from edpm.cli.rm import rm as rm_command
from edpm.cli.pwd import pwd as pwd_command
from edpm.cli.clean import clean as clean_command
from edpm.cli.info import info as info_command
from edpm .cli.config import config as config_command
from edpm .cli.mergedb import mergedb as mergedb_command

edpm_cli.add_command(install_group)
edpm_cli.add_command(find_group)
edpm_cli.add_command(env_group)
edpm_cli.add_command(requirements_command)
edpm_cli.add_command(set_command)
edpm_cli.add_command(rm_command)
edpm_cli.add_command(pwd_command)
edpm_cli.add_command(clean_command)
edpm_cli.add_command(info_command)
edpm_cli.add_command(config_command)
edpm_cli.add_command(mergedb_command)

if __name__ == '__main__':
    edpm_cli()
