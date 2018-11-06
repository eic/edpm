import os
import subprocess
import sys
import utilites

utilites.provide_click_framework()  # Try to import 'click' framework or to reference included version
import click

_abi_name = ""

def get_abi_name():
    """Returns the name for resulting ABI, like Ubuntu """

    global _abi_name
    if not _abi_name:
        result = subprocess.Popen(['perl', 'osrelease.pl'], stdout=subprocess.PIPE, stderr=sys.stderr).communicate()
        _abi_name = result[0].decode('utf-8').strip()
    return _abi_name





class Context:
    # installation dir
    work_dir = ""

    prerequesties = {
        "ubuntu": ["python3-pip, scons, cmake"]
    }


    commands = []

    total_executed_commands = []

    @staticmethod
    def print_self():
        # work_dir
        click.secho("work_dir      :", fg='blue', nl=False)
        click.secho(Context.work_dir)


class PackageInstallationContext:
    """This class stores information which is pretty similar for each package (like directory structure)

    The important here is that while we try to stick to this naming, each package can override them if needed

    """


    def __init__(self, app_name, version_tuple):
        #
        # Root clone branch is like v6-14-04 so we format binary version accordingly
        self.version = 'v{}-{:02}-{:02}'.format(*version_tuple)  # v6-14-04

        #
        # Root general installation directory
        self.app_path = "{glb_app_path}/{app_name}" \
            .format(glb_app_path=Context.work_dir, app_name=app_name)

        #
        # where we download the source or clone git
        self.download_path = "{app_path}/src" \
            .format(app_path=self.app_path)

        #
        # The directory with source files for current version
        self.source_path = "{app_path}/src/{version}" \
            .format(app_path=self.app_path, version=self.version)

        #
        # The directory for cmake build
        self.build_path = "{app_path}/build/{version}" \
            .format(app_path=self.app_path, version=self.version)

        #
        # The directory, where binary is installed
        self.install_path = "{app_path}/bin/{abi_name}" \
            .format(app_path=self.app_path, abi_name=get_abi_name())



class Command:
    """Base abstract class responsible for any command like run, env, etc"""

    def __init__(self):
        self.is_executed = False

    def execute(self):
        """executes the command. Must be implemented in inherited classes"""
        raise NotImplementedError()

    def __str__(self):
        return "Abstract command"


class RunCommand(Command):

    def __init__(self, args):
        super(RunCommand, self).__init__()
        self.args = args
        self.return_code = 1000000

    def execute(self):
        """executes system command"""

        # Print executing command
        click.secho("EXECUTING:", fg='blue', bold=True)
        click.echo(self.args)

        # Execute the command
        self.return_code = subprocess.call(self.args, stdout=sys.stdout, stderr=sys.stderr, shell=True)
        self.is_executed = True

        # Print the result
        click.secho("Execution done. ", fg='blue', bold=True, nl=False)
        click.echo("Return code = ", nl=False)
        click.secho("%i"%self.return_code, fg='red' if self.return_code else 'green', bold=True)


class WorkDirCommand(Command):
    def __init__(self, path):
        super(WorkDirCommand, self).__init__()
        self.path = path

    def execute(self):
        """change directory according to path"""
        click.secho("WORKDIR:", fg='blue', bold=True, nl=False)
        click.echo(self.path)
        os.chdir(self.path)
        self.is_executed = True


class EnvironmentCommand(Command):
    """Sets environment variable"""

    def __init__(self, name, value):
        super(EnvironmentCommand, self).__init__()
        self.name = name
        self.value = value

    def execute(self):
        """ Set environment variable"""

        click.secho("ENV:", fg='blue', bold=True, nl=False)
        click.echo("%s = %s"%(self.name,self.value))
        os.environ[self.name] = self.value
        self.is_executed = True


def run(args):
    Context.commands.append(RunCommand(args))


def workdir(path):
    Context.commands.append(WorkDirCommand(path))


def env(name, value):
    Context.commands.append(EnvironmentCommand(name, value))


def execute_current_plan():
    """Runs all commands saved for running"""

    executed_commands = []
    try:
        for command in Context.commands:
            assert isinstance(command, Command)  # sanity check
            command.execute()  # execute the command!
            executed_commands.append(command)

            # check run command is ended with return code 0
            if command is RunCommand:
                if command.return_code != 0:
                    click.secho("ERROR", fg='red', bold=True, nl=True)
                    click.echo(": Command return code != 0. COMMAND CONTENT:")
                    click.echo(command.args)
                    raise ChildProcessError()

            Context.total_executed_commands.append(command)
    finally:
        for command in Context.commands:
            Context.commands.remove(command)
