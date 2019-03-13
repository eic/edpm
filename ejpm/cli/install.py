import os
import click

from ejpm.cli.ejpm_context import pass_ejpm_context, EjpmContext
from ejpm.engine.db import PacketStateDatabase
from ejpm.engine.output import markup_print as mprint
from ejpm.engine.installation import PacketInstallationInstruction
from ejpm.engine.packet_manager import PacketManager


@click.command()
@click.option('--missing', 'dep_mode', flag_value='missing', help="Installs only missing dependencies", default=True)
@click.option('--single', 'dep_mode', flag_value='single', help="Installs only this package")
@click.option('--all', 'dep_mode', flag_value='all', help="Installs all dependencies by ejpm")
@click.option('--path', 'install_path', default='', help="Is not implemented")
@click.option('--explain', 'just_explain', default=False, is_flag=True, help="Prints what is to be installed (but do nothing)")
@click.option('--deps-only', 'deps_only', default=False, is_flag=True, help="Installs only dependencies but not the packet itself")
@click.argument('name', nargs=1)
@pass_ejpm_context
@click.pass_context
def install(ctx, ectx, dep_mode, name, install_path="", just_explain=False, deps_only=False):
    """Installs packets (and all dependencies)

    \b
    Examples:
      > ejpm install ejana --missing    # install ejana and all missing dependencies
      > ejpm install rave --single      # install just rave package, dependencies are not checked
      > ejpm install ejana --all        # install all ejana dependencies by ejpm
                                        # even if user pointed some deps to external places

    \b
    --explain flag may be used to see what dependencies packet has and what is missing

      > ejpm install ejana --missing --explain   # print what to be installed but not install

    """

    db = ectx.db
    pm = ectx.pm
    assert isinstance(ectx, EjpmContext)
    assert isinstance(db, PacketStateDatabase)
    assert isinstance(pm, PacketManager)

    # Check if packet_name is all, missing or for known packet
    ectx.ensure_packet_known(name)

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
    installer = pm.installers_by_name[name]
    _install_with_deps(ectx, installer.name, mode=dep_mode, just_explain=just_explain, deps_only=deps_only)

    # Update environment scripts if it is not just an explanation
    if not just_explain:
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

    # (!) here we actually install the packet
    try:
        packet.step_install()
    except OSError:
        mprint("<red>Installation stopped because of the error</red>")
        exit(1)

    # if we are here, the packet is installed
    mprint("<green>{} installation step done!</green>\n", packet.name)

    # Add to DB that we installed a packet
    mprint("Adding path to database...\n   This {} installation is set as <blue>selected</blue>", packet.name)

    from ejpm.engine.db import IS_OWNED, IS_ACTIVE, SOURCE_PATH, BUILD_PATH
    updating_data = {
        IS_OWNED: True,
        IS_ACTIVE: True,
        SOURCE_PATH: packet.source_path,
        BUILD_PATH: packet.build_path
    }
    db.update_install(packet.name, packet.install_path, updating_data)
    db.save()


def _install_with_deps(ectx, packet_name, mode, just_explain=False, deps_only=False):
    assert isinstance(ectx, EjpmContext)

    desired_names = ectx.pm.get_installation_names(packet_name, deps_only)

    # First we want to play 'setup' function on all dependencies.
    # This will allow us to build the right environment for non existent packets
    # If this is just a single packet install it will do no harm
    for name in desired_names:
        installer = ectx.pm.installers_by_name[name]
        # To call setup we need some installation path. Those are dependencies and we only know how to
        # install them to top_dir. So we don't care and set simple os.path.join(...)
        installer.setup(os.path.join(ectx.db.top_dir, installer.name))

    #
    # Lets see what is missing and tell it to the user
    missing_packets = []
    mprint("\nCurrent status of the packet and dependencies:")
    for name in desired_names:
        data = ectx.db.get_active_install(name)
        if not data:
            mprint("   <blue>{:<6}</blue> : not installed", name)
            missing_packets.append(name)
        else:
            is_owned_str = '(owned)' if data['is_owned'] else ''
            mprint("   <blue>{:<6}</blue> : {} {}", name, data['install_path'], is_owned_str)

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
        mprint("   <blue>{:<6}</blue> : {}", packet.name, packet.install_path)

    # It is just explanation
    if just_explain:
        return

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
    mprint("\n")
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
                    INSTALL_PATH: ectx.pm.installers_by_name[name].install_path,
                    IS_ACTIVE: True,
                    IS_OWNED: True
                }
        elif mode == 'all':
            # We overwrite installation path for the packet
            inst = {
                INSTALL_PATH: ectx.pm.installers_by_name[name].install_path,
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