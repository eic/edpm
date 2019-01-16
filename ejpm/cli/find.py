from ejpm.cli.ejpm_context import pass_ejpm_context
from ejpm.side_packages import provide_click_framework
from ejpm.engine.db import PacketStateDatabase


provide_click_framework()
import click

@click.group(invoke_without_command=True)
@pass_ejpm_context
@click.pass_context
def find(ctx, ectx):
    assert (isinstance(ectx.db, PacketStateDatabase))
    #if not click.confirm("All packets will be installed here:"):
    #        click.echo('Existing without deleting experiment.')

    db = ectx.db

    click.echo("installed packets:")

    print(db.installed)
    click.echo("missing packets:")
    print(db.missing)

    if not db.top_dir:

        click.echo("Provide the top dir to install things to:")
        click.echo("Run ejpm with --top-dir=<packets top dir>")
        return

    ctx.invoke('root install')



