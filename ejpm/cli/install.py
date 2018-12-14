import os

from ejpm.side_packages import provide_click_framework
from ejpm.engine.db import pass_db, PacketStateDatabase
from ejpm.engine.output import markup_print as mprint
from ejpm.engine.installation import PacketInstallationInstruction

from ejpm.packets.genfit import GenfitInstallation
from ejpm.packets.root_install import RootInstallation
from ejpm.packets import pass_pm, PacketManager

provide_click_framework()
import click


@click.group(invoke_without_command=True)
@click.option('--path', 'install_path', default='')
@click.argument('packet_name', nargs=1)
@pass_pm
@pass_db
@click.pass_context
def install(ctx, db, pm, packet_name, install_path=""):
    """Installs packets"""

    assert isinstance(db, PacketStateDatabase)
    assert isinstance(pm, PacketManager)

    if packet_name in pm.packets.keys():
        _install_packet(db, pm.packets[packet_name], install_path)
    else:
        print("Packet with name '{}' is not found".format(packet_name))
        raise click.Abort()

    if not db.top_dir:
        _print_help_no_top_path()
        raise click.Abort()


    if ctx.invoked_subcommand is None:
        click.echo('I was invoked without subcommand')
    else:
        click.echo('I am about to invoke %s' % ctx.invoked_subcommand)


def _install_packet(db, packet, install_path):
    """Installs packet using its 'installation instruction' class


        :var db: State database
        :type db: PacketStateDatabase
        :var packet: thing that knows how to install a packet
        :type packet: PacketInstallationInstruction
        :var install_path: Path to install app to. If empty {db.top_dir}/{packet.name} is used
        :type install_path: str
    
    """

    assert isinstance(packet, PacketInstallationInstruction)
    assert isinstance(db, PacketStateDatabase)
    if not install_path:
        install_path = os.path.join(db.top_dir, packet.name)

    # set_app_path setups parameters (formats all string variables) for this particular path
    packet.set_app_path(install_path)

    # Pretty header
    mprint("<magenta>=========================================</magenta>")
    mprint("<green> INSTALLING</green> : <blue>{}</blue>", packet.name)
    mprint("<magenta>=========================================</magenta>\n")

    # (!) here we actually install thie package
    try:
        packet.step_install()
    except OSError:
        mprint("<red>Installation stopped because of the error</red>")
        exit(1)

    # if we are here, the packet is installed
    mprint("<green>Root installation step done!</green>\n")
    mprint("Adding path to database...\n   This {} installation is set as <blue>selected</blue>", packet.name)

    # Add to DB that we installed a packet
    db.update_install(packet.name, packet.install_path, is_ejpm_owned=True, is_selected=True)
    db.save()


def _print_help_no_top_path():
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
