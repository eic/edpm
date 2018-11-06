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

    global file_path, click_license_message_is_printed

    try:
        import click
        # everything goes smooth, no need to do anything else
    except ImportError as ex:

        # Since User didn't install click framework, we should write about click license
        if not click_license_message_is_printed:
            click_license_message_is_printed = True
            print("No 'click' framework is installed. Using embedded version. Since that, read the license")
            print("https://click.palletsprojects.com/en/7.x/license/")

        # Add embedded click paket to python search path
        print(os.path.join(file_dir, "side_packages", "_click"))
        sys.path.append(os.path.join(file_dir, "side_packages", "_click"))

        # Now try to import click
        try:
            import click
        except ImportError as ex:
            utilites.print_install_click_msg()
            exit(1)




