import os

from ejpm.side_packages import provide_click_framework
from ejpm.engine.db import pass_db, PacketStateDatabase, IS_SELECTED
from ejpm.engine.output import markup_print as mprint
from ejpm.engine.installation import PacketInstallationInstruction

from ejpm.packets import pass_pm, PacketManager

provide_click_framework()
import click


@click.group(invoke_without_command=True)
@pass_pm
@pass_db
@click.pass_context
def env(ctx, db, pm):
    """Installs packets"""

    assert isinstance(db, PacketStateDatabase)
    assert isinstance(pm, PacketManager)

    if ctx.invoked_subcommand is None:
        names_order = ['root', 'rave', 'genfit', 'jana', 'ejana']

        name_paths = {}
        for name in names_order:
            path, _ = db.get_active_install(name)
            if path is None:
                print("# (!) no active path for {}. Skipping environment!".format(name))
            else:
                name_paths[name]=path

        if name_paths:
            print(pm.gen_bash_environment(name_paths))

    else:
        pass
        # click.echo('I am about to invoke %s' % ctx.invoked_subcommand)
