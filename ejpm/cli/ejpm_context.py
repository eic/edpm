import inspect
import io
import os
import click
import appdirs


from ejpm.engine.db import PacketStateDatabase
from ejpm.engine.packet_manager import PacketManager
from ejpm.engine.output import markup_print as mprint
from ejpm.engine.py23 import to_unicode

EJPM_HOME_PATH = 'ejpm_home_path'       # Home path of the EJPM
EJPM_DATA_PATH = 'ejpm_data_path'       # Path where
DB_FILE_PATH = 'db_file_path'           # Database file path
ENV_SH_PATH = 'env_sh_path'             # SH environment generated file path
ENV_CSH_PATH = 'env_csh_path'           # CSH environment generated file path


class EjpmContext(object):
    """This class holds data that is provided to most EJPM CLI commands"""

    def __init__(self):
        self.db = PacketStateDatabase()
        self.pm = PacketManager()
        self.config = {}
        self._set_paths()

    def load_shmoad_ugly_toad(self):
        """Load the state from disk. DB and packet installers"""

        db_existed = self.load_db_if_exists()   # Try to load the DB

        self.pm.load_installers()               # load installers

        # Update DB "known installers"
        self.db.known_packet_names = self.pm.installers_by_name.keys()

        return db_existed

    def load_db_if_exists(self):
        if self.db.exists():
            self.db.load()
            return True
        return False

    def ensure_db_exists(self):
        """Check if DB exist, create it or aborts everything


         All ensure_xxx functions check the problem, fix it or write message and call Click.Abort()
         """
        # save DB no db...
        if not self.db.exists():
            mprint("<green>creating database...</green>")
            self.db.save()

    def ensure_packet_known(self, packet_name):
        """Check if packet_name is of known packets or aborts everything

           All ensure_xxx functions check the problem, fix it or write message and call Click.Abort()
        """

        # Check if packet_name is all, missing or for known packet
        names = [to_unicode(n) for n in self.pm.installers_by_name.keys()]
        is_valid_packet_name = to_unicode(packet_name) in names

        if not is_valid_packet_name:
            print("Packet with name '{}' is not found".format(packet_name))  # don't know what to do
            raise click.Abort()

    def ensure_tag_known(self, packet_name):
        """Check if packet_name is of known packets or aborts everything

           All ensure_xxx functions check the problem, fix it or write message and call Click.Abort()
        """

        # Check if packet_name is all, missing or for known packet
        is_valid_packet_name = packet_name in self.pm.installers_by_tags.keys()

        if not is_valid_packet_name:
            print("Packet or tag with name '{}' is not found".format(packet_name))  # don't know what to do
            raise click.Abort()

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

    def _set_paths(self):
        """Sets ejpm paths"""

        # EJPM home path
        # call 3 times dirname as we have <db path>/ejpm/cli
        ejpm_home_path = os.path.dirname(os.path.dirname(os.path.dirname(inspect.stack()[0][1])))
        self.config[EJPM_HOME_PATH] = ejpm_home_path

        ejpm_source_stack_path = os.path.join(ejpm_home_path, 'ejpm', 'packets')
        ejpm_source_stack_package = 'ejpm.packets'

        #
        # EJPM data path. It is where db.json and environment files are located
        # We try to read it from EJPM_DATA_PATH environment variable and then use standard (XDG) location
        if 'EJPM_DATA_PATH' in os.environ:
            ejpm_data_path = os.environ['EJPM_DATA_PATH']
            # We don't care if the directory exist as if user provides EJPM_DATA_PATH he is responsible
        else:
            # Get the default (XDG or whatever) standard path to store user data
            ejpm_data_path = appdirs.user_data_dir("ejpm", "Dmitry Romanov")

            # In this case we care and create the directory
            if not os.path.isdir(ejpm_data_path):
                from ejpm.engine.commands import run
                run('mkdir -p "{}"'.format(ejpm_data_path))

        self.config[EJPM_DATA_PATH] = ejpm_data_path

        #
        # Database path
        self.db.file_path = os.path.join(ejpm_data_path, "db.json")
        self.config[DB_FILE_PATH] = self.db.file_path

        #
        # environment script paths
        self.config[ENV_SH_PATH] = os.path.join(ejpm_data_path, "env.sh")
        self.config[ENV_CSH_PATH] = os.path.join(ejpm_data_path, "env.csh")


# Create a database class and @pass_db decorator so our commands could use it
pass_ejpm_context = click.make_pass_decorator(EjpmContext, ensure=True)
