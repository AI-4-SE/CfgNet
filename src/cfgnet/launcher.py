import os
import sys
import time
import logging
import json
from typing import List
import click

from cfgnet.utility import logger
from cfgnet.network.network import Network
from cfgnet.network.network_configuration import NetworkConfiguration
from cfgnet.launcher_configuration import LauncherConfiguration
from cfgnet.analyze.analyzer import Analyzer
from cfgnet.linker.linker_manager import LinkerManager


add_project_root_argument = click.argument(
    "project_root", type=click.Path(exists=True)
)

add_enable_linker_option = click.option(
    "--enable-linker",
    type=click.Choice(LinkerManager.get_linker_names()),
    multiple=True,
    default=LinkerManager.get_linker_names,
    help="Specify a linker to be enabled.  If this is not specified, all "
    "available linkers except those explicitly disabled will be used.  "
    "To enable multiple linkers, pass the option for each of them, i.e.  "
    "`--enable-linker foo --enable-linker bar`.",
)
add_disable_linker_option = click.option(
    "--disable-linker",
    type=click.Choice(LinkerManager.get_linker_names()),
    multiple=True,
    default=[],
    help="Specify a linker to be disabled."
    "To enable multiple linkers, pass the option for each of them, i.e.  "
    "`--disable-linker foo --disable-linker bar`.",
)


@click.group()
@click.option(
    "-v", "--verbose", help="Log everything to console.", is_flag=True
)
def main(verbose: bool):
    LauncherConfiguration.verbose = verbose
    logger.configure_console_logger(verbose=verbose)


@main.command()
@click.option("-b", "--enable-static-blacklist", is_flag=True)
@click.option("-i", "--enable-internal-links", is_flag=True)
@click.option("-c", "--enable-all-conflicts", is_flag=True)
@click.option("-s", "--system_level", is_flag=False)
@click.option("-f", "--config-files", multiple=True)
@add_project_root_argument
@add_enable_linker_option
@add_disable_linker_option
def init(
    enable_static_blacklist: bool,
    enable_internal_links: bool,
    enable_all_conflicts: bool,
    system_level: bool,
    project_root: str,
    enable_linker: List[str],
    disable_linker: List[str],
    config_files: List,
):
    """Initialize configuration network."""
    project_name = os.path.basename(project_root)
    logging.info("Initialize configuration network for %s.", project_name)

    network_configuration = NetworkConfiguration(
        project_root_abs=os.path.abspath(project_root),
        config_files=list(config_files),
        enable_static_blacklist=enable_static_blacklist,
        enable_internal_links=enable_internal_links,
        enabled_linkers=list(set(enable_linker) - set(disable_linker)),
        enable_all_conflicts=enable_all_conflicts,
        system_level=system_level,
    )
    LinkerManager.set_enabled_linkers(network_configuration.enabled_linkers)
    logger.configure_repo_logger(network_configuration.logfile_path())

    start = time.time()

    network = Network.init_network(network_configuration)

    network.save()

    completion_time = round((time.time() - start), 2)

    logging.info("Done in [%s s]", str(completion_time))


@main.command()
@add_project_root_argument
def validate(project_root: str):
    """Validate a reference network against a new network."""
    project_name = os.path.basename(project_root)
    logging.info("Validate configuration network for %s.", project_name)

    start = time.time()

    ref_network = Network.load_network(project_root=project_root)
    logger.configure_repo_logger(ref_network.cfg.logfile_path())

    # TODO Network should configure LinkerManager with list of enabled linkers

    conflicts, new_network = ref_network.validate()

    new_network.save()

    if len(conflicts) == 0:
        logging.info("No conflicts detected.")
        return

    detected_conflicts = sum((conflict.count() for conflict in conflicts))

    logging.error(
        "Detected %s configuration conflicts", str(detected_conflicts)
    )

    completion_time = round((time.time() - start), 2)

    logging.info("Done in [%s s]", completion_time)

    print()
    for conflict in conflicts:
        print(conflict)

    sys.exit(1)


@main.command()
@click.option("-b", "--enable-static-blacklist", is_flag=True)
@click.option("-i", "--enable-internal-links", is_flag=True)
@click.option("-c", "--enable-all-conflicts", is_flag=True)
@click.option("-f", "--config-files", multiple=True)
@click.option("-s", "--system_level", multiple=True)
@add_project_root_argument
@add_enable_linker_option
@add_disable_linker_option
def analyze(
    enable_static_blacklist: bool,
    enable_internal_links: bool,
    enable_all_conflicts: bool,
    project_root: str,
    enable_linker: List[str],
    disable_linker: List[str],
    config_files: List,
    system_level: bool,
):
    """Run self-evaluating analysis of commit history."""
    project_name = os.path.basename(project_root)

    logging.info("Analyzing commit history for %s.", project_name)

    network_configuration = NetworkConfiguration(
        project_root_abs=os.path.abspath(project_root),
        config_files=list(config_files),
        enable_static_blacklist=enable_static_blacklist,
        enable_internal_links=enable_internal_links,
        enabled_linkers=list(set(enable_linker) - set(disable_linker)),
        enable_all_conflicts=enable_all_conflicts,
        system_level=system_level,
    )
    LinkerManager.set_enabled_linkers(network_configuration.enabled_linkers)
    logger.configure_repo_logger(network_configuration.logfile_path())

    enabled_linkers = set(enable_linker) - set(disable_linker)
    LinkerManager.set_enabled_linkers(enabled_linkers)

    start = time.time()

    analyzer = Analyzer(cfg=network_configuration)

    analyzer.analyze_commit_history()

    completion_time = round((time.time() - start), 2)

    logging.info(
        "Analysis of %s done in [%s s].", project_name, completion_time
    )


@main.command()
@click.option("-o", "--output", required=True)  # TODO type
@click.option("-f", "--format", "export_format", required=True)  # TODO type
@click.option("-u", "--include-unlinked", is_flag=True)  # TODO type
@click.option("-v", "--visualize-dot", is_flag=True)  # TODO type
@add_project_root_argument
def export(
    output: str,
    export_format: str,
    include_unlinked: bool,
    visualize_dot: bool,
    project_root: str,
):
    """Export a configuration network."""
    LauncherConfiguration.export_output = output
    LauncherConfiguration.export_format = export_format
    LauncherConfiguration.export_include_unlinked = include_unlinked
    LauncherConfiguration.export_visualize_dot = visualize_dot

    network = Network.load_network(project_root)
    logger.configure_repo_logger(network.cfg.logfile_path())

    if LauncherConfiguration.export_visualize_dot:
        logging.info("Visualize the configuration network.")

        network.visualize(
            name=LauncherConfiguration.export_output,
            export_format=LauncherConfiguration.export_format,
            include_unlinked=LauncherConfiguration.export_include_unlinked,
        )
        return

    logging.info("Export the configuration network.")

    network.export(
        name=LauncherConfiguration.export_output,
        export_format=LauncherConfiguration.export_format,
        include_unlinked=LauncherConfiguration.export_include_unlinked,
    )


@main.command()
@click.option("-f", "--config-files", multiple=True)
@click.option("-o", "--output", required=True)
@click.option("-f", "--system_level", is_flag=False)
@add_project_root_argument
def extract(
    project_root: str, config_files: List, output: str, system_level: bool
):
    """Extract key-value pairs."""
    project_name = os.path.basename(project_root)
    logging.info("Extract key-value pairs for %s.", project_name)

    network_configuration = NetworkConfiguration(
        project_root_abs=os.path.abspath(project_root),
        config_files=list(config_files),
        enable_static_blacklist=False,
        enable_internal_links=False,
        enable_all_conflicts=False,
        system_level=system_level,
    )

    start = time.time()

    network = Network.init_network(network_configuration)

    key_value_pairs = network.get_pairs()

    output_path = os.path.join(
        output, network_configuration.project_name() + "_options.json"
    )

    logging.info("Store key-value pairs in %s.", output_path)

    with open(output_path, "w", encoding="utf-8") as dest:
        json.dump(key_value_pairs, dest, sort_keys=True, indent=4)

    completion_time = round((time.time() - start), 2)

    logging.info("Done in [%s s]", str(completion_time))


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
