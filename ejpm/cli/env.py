import click

from ejpm.cli.ejpm_context import pass_ejpm_context, EjpmContext
from ejpm.engine.db import PacketStateDatabase
from ejpm.packets import PacketManager


@click.group(invoke_without_command=True)
@pass_ejpm_context
@click.pass_context
def env(ctx, ectx):
    """Installs packets"""

    assert isinstance(ectx, EjpmContext)

    # Packet state database
    db = ectx.db
    assert isinstance(db, PacketStateDatabase)

    # Packet manager
    pm = ectx.pm
    assert isinstance(pm, PacketManager)

    # check if DB file already exists
    if not db.exists():
        print("Database doesn't exist. 'env' command has nothing to do")
        return

    if ctx.invoked_subcommand is None:
        print(ectx.pm.gen_bash_env_text(db.get_active_installs()))

    else:
        pass
        # click.echo('I am about to invoke %s' % ctx.invoked_subcommand)
