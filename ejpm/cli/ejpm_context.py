import inspect
import io
import os

from ejpm.engine.db import PacketStateDatabase
from ejpm.packets import PacketManager
from ejpm.side_packages import provide_click_framework

# Try to import 'click' framework or to reference included version
provide_click_framework()  # Try to import 'click' framework or to reference included version
import click


EJPM_HOME_PATH = 'ejpm_home_path'       # Home path of the EJPM
DB_FILE_PATH = 'db_file_path'           # Database file path
ENV_SH_PATH = 'env_sh_path'             # SH environment generated file path
ENV_CSH_PATH = 'env_csh_path'           # CSH environment generated file path


class EjpmContext(object):
    """This class holds data that is provided to most EJPM CLI commands"""

    def __init__(self):
        self.db = PacketStateDatabase()
        self.pm = PacketManager()
        self.config = {}

        # EJPM home path
        # call 3 times dirname as we have <db path>/ejpm/cli
        ejpm_home_path = os.path.dirname(os.path.dirname(os.path.dirname(inspect.stack()[0][1])))
        self.config[EJPM_HOME_PATH] = ejpm_home_path

        #
        # Database path
        self.db.file_path = os.path.join(ejpm_home_path, "db.json")
        self.config[DB_FILE_PATH] = self.db.file_path

        #
        # environment script paths
        self.config[ENV_SH_PATH] = os.path.join(ejpm_home_path, "env.sh")
        self.config[ENV_CSH_PATH] = os.path.join(ejpm_home_path, "env.csh")

    def save_shell_environ(self, file_path, shell):
        """Generates and saves shell environment to a file
        :param file_path: Path to file
        :param shell: 'bash' or 'csh'

        """

        with io.open(file_path, 'w', encoding='utf8') as outfile:    # Write file
            # Make it work for Python 2+3 and with Unicode
            try:
                # noinspection PyUnresolvedReferences
                to_unicode = unicode
            except NameError:
                to_unicode = str
            outfile.write(to_unicode(self.pm.gen_shell_env_text(self.db.get_active_installs(), shell=shell)))

    def save_default_bash_environ(self):
        """Generates and saves bash environment to a default file path"""
        self.save_shell_environ(self.config[ENV_SH_PATH], 'bash')

    def save_default_csh_environ(self):
        """Generates and saves csh/tcsh environment to a default file path"""
        self.save_shell_environ(self.config[ENV_CSH_PATH], 'csh')







# Create a database class and @pass_db decorator so our commands could use it
pass_ejpm_context = click.make_pass_decorator(EjpmContext, ensure=True)
