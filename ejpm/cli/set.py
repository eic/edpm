import os

import click

from ejpm.cli.ejpm_context import pass_ejpm_context, EjpmContext
from ejpm.engine.db import INSTALL_PATH
from ejpm.engine.output import markup_print as mprint


# @click.group(invoke_without_command=True)
@click.command()
@click.argument('packet_name', nargs=1)
@click.argument('install_path', nargs=1)
@pass_ejpm_context
@click.pass_context
def set(ctx, ectx, packet_name, install_path):
    """Sets packets"""

    assert isinstance(ectx, EjpmContext)

    # We need DB ready for this cli command
    ectx.ensure_db_exists()

    # Check that the packet name is from known packets
    ectx.ensure_packet_known(packet_name)

    # update_install will add or update the packet install. We set it active as it make sense...
    ectx.db.update_install(packet_name, install_path, is_active=True)
    ectx.db.save()

    # Update environment scripts
    mprint("Updating environment script files...\n")
    ectx.save_default_bash_environ()
    ectx.save_default_csh_environ()
