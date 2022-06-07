import os
from pathlib import Path

from dataclasses import dataclass, field
from typing import List


@dataclass()
class NetworkConfiguration:
    # Absolute path to project root
    project_root_abs: str
    enable_static_blacklist: bool = False
    enable_dynamic_blacklist: bool = False
    enable_internal_links: bool = False
    # Enable machine learning plugins
    enable_ml_plugins: bool = False
    # Only allow the use of concept plugins
    only_concept_plugins: bool = False
    # Path to CfgNet data directory relative to project_root
    cfgnet_path_rel: str = ".cfgnet"
    # List of names of enabled linkers
    enabled_linkers: List[str] = field(default_factory=list)

    def data_dir_path(self):
        if Path(self.project_root_abs).is_file():
            return os.path.dirname(self.project_root_abs)
        return os.path.join(self.project_root_abs, self.cfgnet_path_rel)

    def network_dir_path(self):
        return os.path.join(self.data_dir_path(), "network")

    def export_dir_path(self):
        return os.path.join(self.data_dir_path(), "export")

    def ignorefile_path(self):
        return os.path.join(self.data_dir_path(), "ignore")

    def project_name(self):
        if Path(self.project_root_abs).is_file():
            return os.path.basename(self.project_root_abs).split(".")[0]
        return os.path.basename(self.project_root_abs)

    def logfile_path(self):
        if Path(self.project_root_abs).is_file():
            file_name = self.project_name()
            dir_path = os.path.dirname(self.project_root_abs)
            return os.path.join(dir_path, f"{file_name}.log")
        return os.path.join(self.data_dir_path(), f"{self.project_name()}.log")

    def statistic_path(self):
        if Path(self.project_root_abs).is_file():
            return self.data_dir_path()
        return os.path.join(self.data_dir_path(), "statistics")
