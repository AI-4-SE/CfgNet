import os

from dataclasses import dataclass, field
from typing import List


@dataclass()
class NetworkConfiguration:
    # Absolute path to project root
    project_root_abs: str
    enable_static_blacklist: bool
    enable_internal_links: bool
    enable_all_conflicts: bool
    system_level: bool
    # Path to CfgNet data directory relative to project_root
    cfgnet_path_rel: str = ".cfgnet"
    # List of names of enabled linkers
    enabled_linkers: List[str] = field(default_factory=list)
    config_files: List[str] = field(default_factory=list)

    def data_dir_path(self):
        return os.path.join(self.project_root_abs, self.cfgnet_path_rel)

    def network_dir_path(self):
        return os.path.join(self.data_dir_path(), "network")

    def export_dir_path(self):
        return os.path.join(self.data_dir_path(), "export")

    def ignorefile_path(self):
        return os.path.join(self.data_dir_path(), "ignore")

    def project_name(self):
        return os.path.basename(self.project_root_abs)

    def logfile_path(self):
        return os.path.join(self.data_dir_path(), f"{self.project_name()}.log")
