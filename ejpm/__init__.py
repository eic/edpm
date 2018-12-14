import inspect
import os
import sys

from ejpm.side_packages import provide_click_framework, provide_ansimarkup
from ejpm.engine.db import pass_db, PacketStateDatabase

# Try to import 'click' framework or to reference included version
provide_click_framework()   # Try to import 'click' framework or to reference included version
import click


def print_first_time_message():
    click.echo("The database file doesn't exist. Probably you run 'ejpm' for the first time.")
    click.echo("Here are your options:\n"
               "\n"
               )
    click.echo("   1. Install all missing packets with 'all' command:")
    click.echo("   ejpm all --top-path=<path>".format(sys.argv[0]))
    click.echo("   Your working directory now is:")
    click.echo("   " + os.getcwd())
    click.echo("   If you intend to install everything in this directory: ".format(sys.argv[0]))
    click.echo('   {} all --top-path="{}"'.format(sys.argv[0], os.getcwd()))
    click.echo("   Note, that by intend top-path is set only once.")
    click.echo(sys.argv)
    click.echo()


_starting_workdir = ""


def _on_start():
    """Steps required in the beginning to run the app"""

    # add ansimarkup to python search path
    # ansimarkup allows to print console messages like <red>text</red>
    #add_ansimarkup_path()

    # Save the initial working directory
    # It is going to be restored in _on_close function
    global _starting_workdir
    _starting_workdir = os.getcwd()


def _on_close():
    """Finalizing function that is called after all commands"""

    # Restore the initial working directory if needed
    if _starting_workdir and _starting_workdir != os.getcwd():
        os.chdir(_starting_workdir)


@click.group(invoke_without_command=True)
@click.option('--debug/--no-debug', default=False)
@click.option('--top-dir', default="")
@pass_db
@click.pass_context
def ejpm_cli(ctx, db, debug, top_dir):
    """EJPM stands for
    """

    # Run initialization stuff
    _on_start()

    # Add _on_close function that will restore working directory
    ctx.call_on_close(_on_close)

    #
    # Now the database...
    assert(isinstance(db, PacketStateDatabase))

    # by default, db file should be at the same place as ejpm.py. Parent of dir of this file
    db_file_dir = os.path.dirname(os.path.dirname(inspect.stack()[0][1]))
    db.file_path = os.path.join(db_file_dir, "db.json")

    # did user asks us to set the top dir
    if top_dir:
        db.top_dir = top_dir
        db.save()

    # check if DB file already exists
    if not db.exists():
        print_first_time_message()
        exit(0)

    # load  the database state
    db.load()

    if ctx.invoked_subcommand is None:
        pass
        # click.echo('I was invoked without subcommand')
    else:
        pass
        # click.echo('I am about to invoke %s' % ctx.invoked_subcommand)

    #click.echo('Debug mode is %s' % ('on' if debug else 'off'))


from ejpm.cli.jana import jana as jana_group
from ejpm.cli.root import root as root_group
from ejpm.cli.install import install as install_group
from ejpm.cli.find import find as find_group


ejpm_cli.add_command(jana_group)
ejpm_cli.add_command(root_group)
ejpm_cli.add_command(install_group)
ejpm_cli.add_command(find_group)

if __name__ == '__main__':
    ejpm_cli()
