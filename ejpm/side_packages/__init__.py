import inspect
import os
import sys

file_path = inspect.stack()[0][1]
file_dir = os.path.dirname(file_path)
click_license_message_is_printed = False


def print_install_click_msg():
    """Prints message of how to install click framework on common platforms"""

    print("Cannot run the 'click' framework. Install it like: ")
    print("   pip install click               # globally")
    print("   pip install --user click        # no global rights needed")
    print("   apt-get install python3-click   # Ubuntu")
    print("   yum install python-click        # RHEL/CentOS")


def provide_click_framework():
    """Function should make available the 'click' framework. Doesn't matter how!"""

    try:
        import click
        # everything goes smooth, no need to do anything else
    except ImportError:

        # Since User didn't install click framework, we should write about click license
        global click_license_message_is_printed
        if not click_license_message_is_printed:
            click_license_message_is_printed = True
            # TODO logging
            # print("No 'click' framework is installed. Using embedded version. Since that, read the license")
            # print("https://click.palletsprojects.com/en/7.x/license/")

        # Add embedded click packet to python search path
        click_packet_path = os.path.join(file_dir, "_click")
        sys.path.append(click_packet_path)

        # Now try to import click
        try:
            import click
        except ImportError:
            print_install_click_msg()
            exit(1)


def provide_ansimarkup():
    """Function should make available the 'ansimarkup'. Doesn't matter how!"""

    try:
        import ansimarkup
        # everything goes smooth, no need to do anything else

    except ImportError:
        # Add embedded framework
        ansimarkup_packet_path = os.path.join(file_dir, "_ansimarkup")
        sys.path.append(ansimarkup_packet_path)

        # Now try to import
        try:
            import click
        except ImportError:
            print_install_click_msg()
