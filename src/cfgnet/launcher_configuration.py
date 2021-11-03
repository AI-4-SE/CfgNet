from dataclasses import dataclass
from typing import Optional


@dataclass()
class LauncherConfiguration:
    # global, for all commands
    verbose: bool = False

    # export
    export_output: Optional[str] = None
    export_format: Optional[str] = None  # TODO: Create format enum in exporter
    export_include_unlinked: bool = False
    export_visualize_dot: bool = False
