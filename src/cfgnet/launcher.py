import click

from cfgnet.network.network import Network
from cfgnet.launcher_configuration import LauncherConfiguration


pass_launcher_configuration = click.make_pass_decorator(
    LauncherConfiguration, ensure=True
)


@click.group()
@click.option(
    "-v", "--verbose", help="Log everything to console.", is_flag=True
)
@click.argument("project_root")
@pass_launcher_configuration
def main(cfg: LauncherConfiguration, project_root: str, verbose: bool):
    cfg.project_root = project_root
    cfg.verbose = verbose


@main.command()
@click.option("-b", "--enable-static-blacklist", is_flag=True)
@click.option("-d", "--enable-dynamic-blacklist", is_flag=True)
@pass_launcher_configuration
def init(
    cfg: LauncherConfiguration,
    enable_static_blacklist: bool,
    enable_dynamic_blacklist: bool,
):
    """Initialize configuration network."""
    cfg.enable_static_blacklist = enable_static_blacklist
    cfg.enable_dynamic_blacklist = enable_dynamic_blacklist

    Network.init_network(cfg.project_root)

    return True


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
