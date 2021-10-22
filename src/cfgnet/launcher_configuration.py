from dataclasses import dataclass
from typing import Optional


@dataclass()
class LauncherConfiguration:
    # global, for all commands
    project_root: str = "."
    verbose: bool = False

    # initialize, analyze
    enable_static_blacklist: bool = False
    enable_dynamic_blacklist: bool = False

    # analyze
    check_network_integrity: bool = False

    # export
    export_output: Optional[str] = None
    export_format: Optional[str] = None  # TODO: Create format enum in exporter
    export_include_unlinked: bool = False
    export_visualize_dot: bool = False


DEFAULT_LAUNCHER_CFG = LauncherConfiguration()  # TODO do we need this?
