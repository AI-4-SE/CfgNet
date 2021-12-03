import os

from dataclasses import dataclass


@dataclass()
class NetworkConfiguration:
    # Absolute path to project root
    project_root_abs: str
    enable_static_blacklist: bool
    enable_dynamic_blacklist: bool
    # Path to CfgNet data directory relative to project_root
    cfgnet_path_rel: str = ".cfgnet"

    def data_dir_path(self):
        return os.path.join(self.project_root_abs, self.cfgnet_path_rel)

    def network_dir_path(self):
        return os.path.join(self.data_dir_path(), "network")

    def export_dir_path(self):
        return os.path.join(self.data_dir_path(), "export")

    def ignorefile_path(self):
        return os.path.join(self.data_dir_path(), "ignore")
