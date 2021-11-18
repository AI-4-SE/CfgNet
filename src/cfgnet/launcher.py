import os
import sys
import time
import logging
import click

from cfgnet.utility.logger import configure_console_logger
from cfgnet.network.network import Network
from cfgnet.network.network_configuration import NetworkConfiguration
from cfgnet.launcher_configuration import LauncherConfiguration


add_project_root_argument = click.argument(
    "project_root", type=click.Path(exists=True)
)


@click.group()
@click.option(
    "-v", "--verbose", help="Log everything to console.", is_flag=True
)
def main(verbose: bool):
    LauncherConfiguration.verbose = verbose
    configure_console_logger(verbose=verbose)


@main.command()
@click.option("-b", "--enable-static-blacklist", is_flag=True)
@click.option("-d", "--enable-dynamic-blacklist", is_flag=True)
@add_project_root_argument
def init(
    enable_static_blacklist: bool,
    enable_dynamic_blacklist: bool,
    project_root: str,
):
    """Initialize configuration network."""
    network_configuration = NetworkConfiguration(
        project_root_abs=os.path.abspath(project_root),
        enable_static_blacklist=enable_static_blacklist,
        enable_dynamic_blacklist=enable_dynamic_blacklist,
    )

    start = time.time()

    network = Network.init_network(network_configuration)

    network.save()

    completion_time = round((time.time() - start), 2)

    # TODO: Replace print with logging
    print(f"Done in {completion_time}s")


@main.command()
@add_project_root_argument
def validate(project_root: str):
    logging.info("Validating network for '%s'.", project_root)

    start = time.time()

    ref_network = Network.load_network(project_root=project_root)

    conflicts, new_network = ref_network.validate()

    new_network.save()

    if len(conflicts) == 0:
        # TODO: Replace print with logging
        print("No conflicts detected.")
        return

    detected_conflicts = sum([conflict.count() for conflict in conflicts])

    # TODO: Replace print with logging
    print(f"Detected {detected_conflicts} configuration conflicts.")

    completion_time = round((time.time() - start), 2)

    # TODO: Replace print with logging
    print(f"Done in {completion_time}s")

    for conflict in conflicts:
        logging.info(conflict)

    sys.exit(1)


@main.command()
@click.option("-b", "--enable-static-blacklist", is_flag=True)
@click.option("-d", "--enable-dynamic-blacklist", is_flag=True)
@add_project_root_argument
def analyze(
    enable_static_blacklist: bool,
    enable_dynamic_blacklist: bool,
    project_root: str,
):
    """Run self-evaluating analysis of commit history."""
    network_configuration = NetworkConfiguration(
        project_root_abs=os.path.abspath(project_root),
        enable_static_blacklist=enable_static_blacklist,
        enable_dynamic_blacklist=enable_dynamic_blacklist,
    )

    # TODO Run analysis

    logging.info(
        "Analyzing network for '%s'.", network_configuration.project_root_abs
    )


@main.command()
@click.option("-o", "--output", required=True)  # TODO type
@click.option("-f", "--format", "export_format", required=True)  # TODO type
@click.option("-u", "--include-unlinked", is_flag=True, help="TODO")
@click.option("--visualize-dot", is_flag=True, help="TODO")
@add_project_root_argument
def export(
    output: str,
    export_format: str,
    include_unlinked: bool,
    visualize_dot: bool,
    project_root: str,  # (TODO remove when implemented) pylint: disable=unused-argument
):
    LauncherConfiguration.export_output = output
    LauncherConfiguration.export_format = export_format
    LauncherConfiguration.export_include_unlinked = include_unlinked
    LauncherConfiguration.export_visualize_dot = visualize_dot

    # TODO network = Network.load_network(project_root)
    # TODO Export


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
