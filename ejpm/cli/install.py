import os

from ejpm.cli.ejpm_context import pass_ejpm_context, EjpmContext
from ejpm.side_packages import provide_click_framework
from ejpm.engine.db import PacketStateDatabase
from ejpm.engine.output import markup_print as mprint
from ejpm.engine.installation import PacketInstallationInstruction
from ejpm.packets import PacketManager

provide_click_framework()
import click


@click.group(invoke_without_command=True)
@click.option('--path', 'install_path', default='')
@click.argument('packet_name', nargs=1)
@pass_ejpm_context
@click.pass_context
def install(ctx, ectx, packet_name, install_path=""):
    """Installs packets"""

    db = ectx.db
    pm = ectx.pm
    assert isinstance(ectx, EjpmContext)
    assert isinstance(db, PacketStateDatabase)
    assert isinstance(pm, PacketManager)

    # Check if packet_name is all, missing or for known packet
    is_valid_packet_name = packet_name in ['all', 'missing'] + pm.packets.keys()

    if not is_valid_packet_name:
        print("Packet with name '{}' is not found".format(packet_name))  # don't know what to do
        raise click.Abort()

    # Ok, looks like we are going to install something

    # If no db...
    if not db.exists():
        mprint("<green>creating database...</green>")
        db.save()

    # Lets check if we have top_dir
    if not db.top_dir:
        _print_help_no_top_path()
        raise click.Abort()

    if packet_name == 'all':
        _update_env_assuming_install_all(ectx)                      # set environment spitting on existing missing
        _install_all(ectx)                                          # install all packets
    if packet_name == 'missing':
        _update_env_assuming_install_missing(ectx)                  # set environment assuming we'll install missing
        _install_missing(ectx)                                      # install only missing packets
    elif packet_name in pm.packets.keys():
        pm.update_python_env(db.get_active_installs())              # get active environment 'as is'
        _install_packet(db, pm.packets[packet_name], install_path)  # install known packet

    # Update environment scripts
    mprint("Updating environment script files...\n")
    ectx.save_default_bash_environ()
    ectx.save_default_csh_environ()

    if ctx.invoked_subcommand is None:
        pass
        # click.echo('I was invoked without subcommand')
    else:
        pass
        # click.echo('I am about to invoke %s' % ctx.invoked_subcommand)


def _install_packet(db, packet, install_path='', replace_active=True):
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

    # Add to DB that we installed a packet
    mprint("Adding path to database...\n   This {} installation is set as <blue>selected</blue>", packet.name)
    db.update_install(packet.name, packet.install_path, is_owned=True, is_active=True)
    db.save()


def _install_non_existent_packet(db, packet, install_path):
    if db.get_active_install_path(packet.name) is not None:
        _install_packet(db, packet, install_path)


def _print_help_no_top_path():
    mprint("<red>(!)</red> installation directory is not set <red>(!)</red>\n"
           "ejpm doesn't know where to install missing packets\n\n"
           "<b><blue>what to do:</blue></b>\n"
           "  Provide the top dir to install things to:\n"
           "     ejpm --top-dir=<path to top dir>\n"
           "  Less recommended. Provide each install command with --path flag:\n"
           "     ejpm install <packet> --path=<path for packet>\n"
           "  (--path=... is not just where binary will be installed,\n"
           "   all related stuff is placed there)\n\n"

           "<b><blue>copy&paste:</blue></b>\n"
           "  to install missing packets in this directory: \n"
           "     ejpm --top-dir=`pwd`\n\n"

           "  to install missing packets to your home directory: \n"
           "     ejpm --top-dir=~/.ejana\n\n")


def _install_all(ectx):
    assert isinstance(ectx, EjpmContext)

    packets = [ectx.pm.packets[name] for name in ectx.dep_order]

    for packet in packets:
        _install_packet(ectx.db, packet)


def _install_missing(ectx):
    assert isinstance(ectx, EjpmContext)

    active_installs = ectx.db.get_active_installs()

    names_to_install = []
    mprint("\nMissing and known packets status:")
    for name, data in active_installs.items():
        if not data:
            mprint("   <blue>{}</blue> - to be installed", name)
            names_to_install.append(name)
        else:
            mprint("   <blue>{}</blue> - at: {}, ", name, data['install_path'])

    packets = [ectx.pm.packets[name] for name in ectx.dep_order if name in names_to_install]

    mprint("\n <b>INSTALLATION ORDER</b>:")
    for packet in packets:
        mprint("   <blue>{}</blue> : {}", packet.name, packet.install_path)

    for packet in packets:
        _install_packet(ectx.db, packet)


def _update_env_assuming_install_missing(ectx):
    """Update python os.environ assuming we will install missing packets"""

    from ejpm.engine.db import IS_OWNED, IS_ACTIVE, INSTALL_PATH
    assert isinstance(ectx, EjpmContext)

    # Go through provided name-path pairs:
    for name, data in ectx.db.get_active_installs().items():

        # There is no installation data for the packet, but we assume we will install it now!
        if not data:
            data = {
                INSTALL_PATH: os.path.join(ectx.db.top_dir, name),
                IS_ACTIVE: True,
                IS_OWNED: True
            }

        # If we have a generator for this program and installation data
        if data and name in ectx.pm.env_generators.keys():
            env_gens = ectx.pm.env_generators[name]
            for env_gen in env_gens(data):          # Go through 'environment generators' look engine/env_gen.py
                env_gen.update_python_env()         # Do environment update


def _update_env_assuming_install_all(ectx):
    """Update python os.environ assuming we will install all packets by ourselves"""

    from ejpm.engine.db import IS_OWNED, IS_ACTIVE, INSTALL_PATH
    assert isinstance(ectx, EjpmContext)

    # Go through provided name-path pairs:
    for name, data in ectx.db.get_active_installs().items():

        # We overwrite data for the packet
        data = {
            INSTALL_PATH: os.path.join(ectx.db.top_dir, name),
            IS_ACTIVE: True,
            IS_OWNED: True
        }

        # If we have a generator for this program and installation data
        if data and name in ectx.pm.env_generators.keys():
            env_gens = ectx.pm.env_generators[name]
            for env_gen in env_gens(data):          # Go through 'environment generators' look engine/env_gen.py
                env_gen.update_python_env()         # Do environment update
