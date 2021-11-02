from dataclasses import dataclass


@dataclass()
class NetworkConfiguration:
    # Absolute path to project root
    project_root_abs: str
    enable_static_blacklist: bool
    enable_dynamic_blacklist: bool
