import os

import click

from ejpm.cli.ejpm_context import pass_ejpm_context, EjpmContext
from ejpm.engine.db import INSTALL_PATH
from ejpm.engine.output import markup_print as mprint

# @click.group(invoke_without_command=True)
@click.command()
@click.argument('os_name', nargs=1, metavar='<os-name>')
@click.argument('args', nargs=-1, metavar='<packet-names>')
@click.option('--optional', 'print_mode', flag_value='optional', help="Print optional packages")
@click.option('--required', 'print_mode', flag_value='required', help="Print required packages")
@click.option('--all', 'print_mode', flag_value='all', help="Print all packages (ready for packet manager install)")
@click.option('--all-titles', 'print_mode', flag_value='all_titles', help="Print all packages (human readable)", default=True)

@pass_ejpm_context
@click.pass_context
def req(ctx, ectx, os_name, args, print_mode):
    """req - Shows required packages that can be installed by operating system.

    \b
    Example:
      req ubuntu ejana
      req fedora ejana
      req fedora root clhep

    By adding --optional, --required, --all flags you can use this command with packet managers:
      req


    """

    assert isinstance(ectx, EjpmContext)

    # We need DB ready for this cli command
    ectx.ensure_db_exists()

    # We have some args, first is os name like 'ubuntu' or 'fedora'
    known_os = ectx.pm.os_deps_by_name['ejana']['required'].keys()

    if os_name not in known_os:
        mprint('<red><b>ERROR</b></red>: name "{}" is unknown\nKnown os names are:', os_name)
        for name in known_os:
            mprint('   {}', name)
        click.echo(ctx.get_help())
        ctx.exit(1)

    # We have something like 'ubuntu ejana'
    if args:
        names = []
        for packet_name in args:                                    # get all dependencies
            ectx.ensure_packet_known(packet_name)
            names += ectx.pm.get_installation_names(packet_name)    # this func returns name + its_deps

        names = list(set(names))                                    # remove repeating names

    else:
        names = ectx.pm.installers_by_name.keys()                   # select all packets

    _print_combined(ectx, os_name, names, print_mode)               # print what we have


def _print_combined(ectx, os_name, packet_names, print_mode):

    required = []
    optional = []
    for name in packet_names:
        required.extend(ectx.pm.os_deps_by_name[name]['required'][os_name].split(' ,'))
        optional.extend(ectx.pm.os_deps_by_name[name]['optional'][os_name].split(' ,'))

    # remove emtpy elements and repeating elements
    required = list(set([r for r in required if r]))
    optional = list(set([o for o in optional if o]))

    # We print titles only if --all-with-titles flag is set
    if print_mode == 'all_titles':
        mprint("<blue><b>REQUIRED</b></blue>:")

    # We print required packets in all cases except --optinal flags
    if print_mode != 'optional':
        mprint(" ".join(required))

    # We print titles only if --all-with-titles flag is set
    if print_mode == 'all_titles':
        mprint("<blue><b>OPTIONAL</b></blue>:")

    # We print optional packets in all cases except --required flags
    if print_mode != 'optional':
        mprint(" ".join(optional))
