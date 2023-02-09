from concurrent.futures import ThreadPoolExecutor, as_completed

import click

from backup_juggler.backup_juggler import (JugglerController, JugglerModel,
                                           JugglerView)


@click.command(
    help='Creation of multiple backups from multiple sources at the same time made easy'
)
@click.argument('sources', nargs=-1, type=click.Path(exists=True))
@click.option(
    '-d',
    '--destinations',
    multiple=True,
    required=True,
    type=click.Path(exists=True),
)
def cli(sources, destinations):
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(backup, source, destination)
            for source in sources
            for destination in destinations
        ]
        for future in as_completed(futures):
            future.result()


def backup(source, destination):
    model = JugglerModel(source, destination)
    view = JugglerView(model)
    controller = JugglerController(model, view)
    controller.do_copy()
