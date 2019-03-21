import os

import click

from ejpm.cli.ejpm_context import pass_ejpm_context, EjpmContext
from ejpm.engine.output import markup_print as mprint


# @click.group(invoke_without_command=True)
@click.command()
@click.argument('packet_name', nargs=-1, metavar='<packet-name>')
@pass_ejpm_context
@click.pass_context
def cd(ctx, ectx, packet_name):
    """Changes current directory to some ejpm related path

    Usage:
        ejpm cd                  # cd-s to ejpm top dir
        ejpm cd <packet-name>    # cd-s to <packet-name> installation dir

    """
    from ejpm.engine.db import INSTALL_PATH, IS_OWNED
    assert isinstance(ectx, EjpmContext)

    # We need DB ready for this cli command
    ectx.ensure_db_exists()

    # Check that the packet name is from known packets
    if not packet_name:
        cd_path = ectx.db.top_dir
    else:
        # Get installation data for the active install
        install_data = ectx.db.get_active_install(packet_name)
        if not install_data:
            mprint("No active installation data found for the packet '{}'", packet_name)
            raise click.Abort()

        # If ejpm 'owns' an installation at this point we assume that parent directory usually is needed
        # Like if ejpm owns 'root' it is assumed that <top-dir>/root is needed rather than <top-dir>/root/root-v6-...
        cd_path = install_data[INSTALL_PATH]
        if install_data[IS_OWNED]:
            cd_path = os.path.pardir(cd_path)

    # change cur dir
    ectx.must_restore_cwd = False   # Don't restore CWD on click exit
    os.chdir(cd_path)



