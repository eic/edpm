import sys
import utilites
import subprocess
from under_the_hood import Context, run, env, workdir, execute_current_plan
import rave as package_rave
import root as package_root

# Try to import 'click' framework or to reference included version
utilites.provide_click_framework()   # Try to import 'click' framework or to reference included version
import click



@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    click.echo('Debug mode is %s' % ('on' if debug else 'off'))
    Context.work_dir = '/home/romanov/jleic/test'


@cli.group(invoke_without_command=True)
@click.pass_context
def rave(ctx):
    """Rave package and its options"""

    if ctx.invoked_subcommand is None:
        print("hihihaha")


@rave.command(name='get')
def rave_get():
    """Downloads rave"""

    context = package_rave.RaveInstallationContext()
    context.step_download()
    execute_current_plan()


@rave.command(name='build')
def rave_build():
    """Builds and installs RAVE"""

    context = package_rave.RaveInstallationContext()
    context.step_build()
    execute_current_plan()


@cli.group(invoke_without_command=True)
@click.pass_context
def root(ctx):
    """CERN ROOT package management"""

    if ctx.invoked_subcommand is None:
        print("CERN ROOT package status... not implemented")


@root.command(name='get')
def root_get():
    """Downloads Cern ROOT"""

    context = package_root.RootInstallationContext()
    context.step_clone_root()
    execute_current_plan()


@root.command(name='build')
def root_build():
    """Builds and installs Cern ROOT"""

    context = package_root.RootInstallationContext()
    context.step_build_root()
    execute_current_plan()

if __name__ == '__main__':
    cli()
