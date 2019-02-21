from ejpm.cli.ejpm_context import pass_ejpm_context, EjpmContext
from side_packages import provide_click_framework
from ejpm.engine.output import markup_print as mprint

provide_click_framework()
import click


# @click.group(invoke_without_command=True)
@click.command()
@click.argument('packet_name', nargs=1)
@click.argument('install_path', nargs=1)
@pass_ejpm_context
@click.pass_context
def install(ctx, ectx, packet_name, install_path):
    """Sets packets"""

    assert isinstance(ectx, EjpmContext)

    # We need DB ready for this cli command
    ectx.ensure_db_exists()

    # Check that the packet name is from known packets
    ectx.ensure_packet_known(packet_name)


    # Update environment scripts
    mprint("Updating environment script files...\n")
    ectx.save_default_bash_environ()
    ectx.save_default_csh_environ()
