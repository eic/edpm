import os
import click

from ejpm.cli.ejpm_context import pass_ejpm_context, EjpmContext
from ejpm.engine.db import PacketStateDatabase
from ejpm.engine.output import markup_print as mprint
from ejpm.engine.installation import PacketInstallationInstruction
from ejpm.packets import PacketManager

#@click.group(invoke_without_command=True)
@click.command()
@click.option('--path', 'install_path', default='')
@click.option('--all', 'dep_mode', flag_value='all')
@click.option('--missing', 'dep_mode', flag_value='missing')
@click.option('--single', 'dep_mode', flag_value='single', default=True)
@click.argument('name', nargs=1)
@pass_ejpm_context
@click.pass_context
def install(ctx, ectx, dep_mode, name, install_path=""):
    """Installs packets"""

    db = ectx.db
    pm = ectx.pm
    assert isinstance(ectx, EjpmContext)
    assert isinstance(db, PacketStateDatabase)
    assert isinstance(pm, PacketManager)

    # Check if packet_name is all, missing or for known packet
    is_valid_packet_name = name in pm.installers_by_tags.keys()

    if not is_valid_packet_name:
        print("Packet with name '{}' is not found".format(name))  # don't know what to do
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

    # Install packets
    # set the tag we want to install
    tag_name, installer = pm.installers_by_tags[name]
    installer.selected_tag = tag_name
    _install_with_deps(ectx, installer.name, installer.required_deps, mode=dep_mode)

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
    packet.setup(install_path)

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
    mprint("<green>{} installation step done!</green>\n", packet.name)

    # Add to DB that we installed a packet
    mprint("Adding path to database...\n   This {} installation is set as <blue>selected</blue>", packet.name)
    db.update_install(packet.name, packet.install_path, is_owned=True, is_active=True)
    db.save()


def _install_with_deps(ectx, packet_name, dep_names, mode):
    assert isinstance(ectx, EjpmContext)

    # If we install just a single packet desired_names a single name
    desired_names = dep_names + [packet_name] if dep_names else [packet_name]

    #
    # Lets see what is missing and tell it to the user
    missing_packets = []
    mprint("\nCurrent status of the packet and dependencies:")
    for name in desired_names:
        data = ectx.db.get_active_install(name)
        if not data:
            mprint("   <blue>{}</blue> - not installed", name)
            missing_packets.append(name)
        else:
            is_owned_str = '(owned)' if data['is_owned'] else ''
            mprint("   <blue>{}</blue> - at: {} {}, ", name, data['install_path'], is_owned_str)

    #
    # Select packets to install. mode tells what we should do with dependencies
    if mode == 'missing':
        # select only missing packets
        install_packets = [ectx.pm.installers_by_name[name] for name in desired_names if name in missing_packets]
    elif mode == 'single':
        # single = we only one packet
        install_packets = [ectx.pm.installers_by_name[packet_name]]
    elif mode == 'all':
        # all - we just overwrite everything
        install_packets = [ectx.pm.installers_by_name[name] for name in desired_names]
    else:
        raise NotImplementedError("installation dependencies mode is not in [missing, single, all]")

    #
    # Is there something to build?
    if not install_packets:
        mprint("Nothing to build and install!")
        return

    # Print user what is going to be built
    mprint("\n <b>INSTALLATION ORDER</b>:")
    for packet in install_packets:
        mprint("   <blue>{}</blue> : {}", packet.name, packet.install_path)

    # Set environment before build
    _update_python_env(ectx, ectx.pm.installers_by_name, mode)  # set environment spitting on existing missing

    #
    for packet in install_packets:
        _install_packet(ectx.db, packet)


def _update_python_env(ectx, dep_order, mode=''):
    """Update python os.environ assuming we will install missing packets"""

    from ejpm.engine.db import IS_OWNED, IS_ACTIVE, INSTALL_PATH
    assert isinstance(ectx, EjpmContext)

    # Pretty header
    mprint("<magenta>=========================================</magenta>")
    mprint("<green> SETTING ENVIRONMENT</green>")
    mprint("<magenta>=========================================</magenta>\n")

    # We will look through database and see, what is 'active installation' of packages
    # Depending on mode, we will try to:
    #    mode     | action
    #   ----------+----------
    #   'missing' | replace missing installations assuming we will install the package
    #   'all'     | replace all packets installation path assuming we will install all by our script
    #   ''        | just skip missing

    inst_by_name = {}
    for name, inst in ectx.db.get_active_installs().items():

        if mode == 'missing':
            # There is no installation data for the packet, but we assume we will install it now!
            if not inst:
                inst = {
                    INSTALL_PATH: os.path.join(ectx.db.top_dir, name),
                    IS_ACTIVE: True,
                    IS_OWNED: True
                }
        elif mode == 'all':
            # We overwrite installation path for the packet
            inst = {
                INSTALL_PATH: os.path.join(ectx.db.top_dir, name),
                IS_ACTIVE: True,
                IS_OWNED: True
            }

        if inst:
            inst_by_name[name] = inst

    for name in dep_order:
        # If we have a generator for this program and installation data
        if name in inst_by_name.keys() and name in ectx.pm.env_generators.keys():
            mprint("<blue><b>Updating python environment for '{}'</b></blue>".format(name))
            env_gens = ectx.pm.env_generators[name]
            for env_gen in env_gens(inst_by_name[name]):   # Go through 'environment generators' look engine/env_gen.py
                env_gen.update_python_env()                # Do environment update


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