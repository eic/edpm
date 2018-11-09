from jepm.side_packages import provide_click_framework

provide_click_framework()

import click


@click.group(invoke_without_command=True)
def jana():
    from jepm.packages import print_classes
    print_classes()


@jana.command()
def version():
    click.echo('2.8')
