from ejpm.side_packages import provide_click_framework
from ejpm.engine.db import pass_db
from ejpm.packets.root_install import RootInstallation


provide_click_framework()
import click


@click.group(invoke_without_command=True)
def root():
    if not click.confirm("All packets will be installed here:"):
        click.echo('Existing without deleting experiment.')



@root.command()
@pass_db
def install(db):
    root_install = RootInstallation(db.top_dir)
    click.echo("Installing root")

