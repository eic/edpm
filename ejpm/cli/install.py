import os

from ejpm.side_packages import provide_click_framework
from ejpm.engine.db import pass_db, PacketStateDatabase
from ejpm.engine.output import markup_print as mprint

from ejpm.packets.root_install import RootInstallationInstruction

provide_click_framework()
import click


@click.group(invoke_without_command=True)
@pass_db
@click.pass_context
def install(ctx, db):
    """Installs packets"""

    assert (isinstance(db, PacketStateDatabase))
    #if not click.confirm("All packets will be installed here:"):
    #        click.echo('Existing without deleting experiment.')

    if not db.top_dir:
        mprint("<red>(!)</red> installation directory is not set <red>(!)</red>\n"
               "ejpm doesn't know where to install missing packets\n\n"
               "<b>what to do:</b>\n"
               "  Provide the top dir to install things to:\n"
               "     ejpm --top-dir=<path to top dir>\n"
               "  Less recommended. Provide each install command with --path flag:\n"
               "     ejpm install <packet> --path=<path for packet>\n"
               "  (--path=... is not just where binary will be installed,\n"
               "   all related stuff is placed there)\n\n"
               
               "<b>copy paste:</b>\n"
               "  to install missing packets in this directory: \n"
               "     ejpm --top-dir=`pwd`\n\n"

               "  to install missing packets to your home directory: \n"
               "     ejpm --top-dir=~/.ejana\n\n")
        exit(1)

    if ctx.invoked_subcommand is None:
        click.echo('I was invoked without subcommand')
    else:
        click.echo('I am about to invoke %s' % ctx.invoked_subcommand)



@install.command()
@pass_db
def root(db):
    """
    Installs CERN ROOT
    """

    assert (isinstance(db, PacketStateDatabase))

    root_path = os.path.join(db.top_dir, "root")
    packet = RootInstallationInstruction(root_path)

    # installation path
    #packet.install()

    mprint("<green>Root installation step done!</green>")
    mprint("Adding path to database...\n   This root installation is set as <blue>selected</blue>")

    db.update_install('root', packet.install_path, is_ejpm_owned=True, is_selected=True)
    db.save()

