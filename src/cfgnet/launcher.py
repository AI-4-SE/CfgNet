import sys
from typing import List, Any
import logging
import click

from cfgnet.launcher_configuration import (
    LauncherConfiguration,
)
from cfgnet.network.network import Network

pass_launcher_configuration = click.make_pass_decorator(
    LauncherConfiguration, ensure=True
)


add_project_root_argument = click.argument(
    "project_root", type=click.Path(exists=True)
)


@click.group()
@click.option(
    "-v", "--verbose", help="Log everything to console.", is_flag=True
)
@pass_launcher_configuration
def main(cfg: LauncherConfiguration, verbose: bool):
    cfg.verbose = verbose


@main.command()
@click.option("-b", "--enable-static-blacklist", is_flag=True)
@click.option("-d", "--enable-dynamic-blacklist", is_flag=True)
@pass_launcher_configuration
@add_project_root_argument
def init(
    cfg: LauncherConfiguration,
    enable_static_blacklist: bool,
    enable_dynamic_blacklist: bool,
    project_root: str,
):
    """Initialize configuration network."""
    cfg.project_root = project_root
    cfg.enable_static_blacklist = enable_static_blacklist
    cfg.enable_dynamic_blacklist = enable_dynamic_blacklist

    logging.info("Initializing network for '%s'.", cfg.project_root)

    Network.init_network(cfg.project_root)


@main.command()
@pass_launcher_configuration
@add_project_root_argument
def validate(
    cfg: LauncherConfiguration,
    project_root: str,
):
    cfg.project_root = project_root

    logging.info("Validating network for '%s'.", cfg.project_root)

    # TODO network: Network = Network.load_network(cfg)

    # TODO Change Any to Conflict once conflict class is added
    # TODO replace empty list with call to `network.validate()`
    conflicts: List[Any] = []

    if len(conflicts) == 0:
        logging.info("No conflicts detected. Updated reference network.")
        # TODO network.save(cfg)
        return

    logging.error(
        "Detected %d configuration conflicts.",
        sum([conflict.count() for conflict in conflicts]),
    )

    for conflict in conflicts:
        print(conflict)

    sys.exit(1)


@main.command()
@click.option("-b", "--enable-static-blacklist", is_flag=True)
@click.option("-d", "--enable-dynamic-blacklist", is_flag=True)
@pass_launcher_configuration
@add_project_root_argument
def analyze(
    cfg: LauncherConfiguration,
    enable_static_blacklist: bool,
    enable_dynamic_blacklist: bool,
    project_root: str,
):
    """Run self-evaluating analysis of commit history."""
    cfg.project_root = project_root
    cfg.enable_static_blacklist = enable_static_blacklist
    cfg.enable_dynamic_blacklist = enable_dynamic_blacklist

    logging.info("Analyzing network for '%s'.", cfg.project_root)

    # TODO Network.analyze(cfg)


@main.command()
@click.option("-o", "--output", required=True)  # TODO type
@click.option("-f", "--format", "export_format", required=True)  # TODO type
@click.option("-u", "--include-unlinked", is_flag=True, help="TODO")
@click.option("--visualize-dot", is_flag=True, help="TODO")
@pass_launcher_configuration
@add_project_root_argument
def export(
    cfg: LauncherConfiguration,
    output: str,
    export_format: str,
    include_unlinked: bool,
    visualize_dot: bool,
    project_root: str,
):
    cfg.project_root = project_root
    cfg.export_output = output
    cfg.export_format = export_format
    cfg.export_include_unlinked = include_unlinked
    cfg.export_visualize_dot = visualize_dot

    logging.info("Exporting network for '%s'.", cfg.project_root)

    # TODO network = Network.load_network(cfg)
    # TODO network.export(cfg)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
