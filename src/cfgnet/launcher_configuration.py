from dataclasses import dataclass
from typing import Optional


@dataclass()
class LauncherConfiguration:
    project_root: str = "."
    verbose: bool = False
    enable_static_blacklist: Optional[bool] = None
    enable_dynamic_blacklist: Optional[bool] = None
