from jepm.side_packages import provide_click_framework
from jepm.under_the_hood.db import pass_db, PacketStateDatabase

# Try to import 'click' framework or to reference included version
provide_click_framework()   # Try to import 'click' framework or to reference included version
import click


def print_first_time_message():
    click.echo("The database file doesn't exist, wich probably means you are running this tool for the first time")




@click.group()
@click.option('--debug/--no-debug', default=False)
@pass_db
def jepm_cli(db, debug):
    """Runs command line interface"""
    """And even something else"""

    assert(isinstance(db, PacketStateDatabase))

    if not db.exists():

    db.load()

    click.echo('Debug mode is %s' % ('on' if debug else 'off'))


from jepm.cli.jana import jana as jana_goup

jepm_cli.add_command(jana_goup)

if __name__ == '__main__':
    jepm_cli()