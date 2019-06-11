import click
from ejpm.cli.ejpm_context import pass_ejpm_context, EjpmContext

@click.command()
@click.argument('name_values', nargs=-1)
@pass_ejpm_context
@click.pass_context
def config(ctx, ectx, name_values):
    """Sets build config for a packet

    If packet name is put, config goes into that packet. If no packet name is provided,
    config goes into global_config which affects all packet installations.

    Example:
        build_threads=4 jana branch=greenfield

    Explanation: global parameter 'build_threads' is set to 4, and 'jana' parameter  branch is set to 'greenfield'

    The example above is an extreme use case of this command and it is advised to split the contexts:
    >> ejpm config build_threads=4
    >> ejpm config jana branch=greenfield
    """

    assert isinstance(ectx, EjpmContext)

    # We need DB ready for this cli command
    ectx.ensure_db_exists()

    # Check that the packet name is from known packets
    config_blob = _process_name_values(name_values)

    for context_name in config_blob.keys():
        if context_name == 'global':
            config = ectx.db.get_global_config()
        else:
            ectx.ensure_installer_known(context_name)
            config = ectx.db.get_config(context_name)

        config.update(config_blob[context_name])    # update config
        ectx.db.save()                              # save config


def _process_name_values(name_values):
    """Converts input parameters to a config map

    >>> _process_name_values(['build_threads=4', 'jana', 'branch=greenfield',  'build_threads=1'])
    {'global': [{'build_threads': '4'}], 'jana': [{'branch': 'greenfield'}, {'build_threads': '1'}]}

    """

    context = 'global'
    result = {context: []}

    for name_value in name_values:
        if '=' in name_value:
            name, value = tuple(name_value.split('='))
            result[context].append({name:value})
        else:
            context = name_value
            if context not in result.keys():
                result[context] = []

    return result
