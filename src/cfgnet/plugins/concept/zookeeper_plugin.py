import os
from cfgnet.config_types.config_types import ConfigType
from cfgnet.plugins.file_type.configparser_plugin import ConfigParserPlugin


class ZookeeperPlugin(ConfigParserPlugin):
    def __init__(self):
        super().__init__("zookeeper")

    def is_responsible(self, abs_file_path: str) -> bool:
        file_name = os.path.basename(abs_file_path)
        return file_name == "zoo.cfg"

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        option_name = option_name.lower()

        if option_name.endswith(("port")):
            return ConfigType.PORT

        if option_name.endswith(("dir", "file")):
            return ConfigType.PATH

        if option_name.endswith(("limit", "size", "buffer")):
            return ConfigType.SIZE

        if option_name.endswith(("address")):
            return ConfigType.IP_ADDRESS

        if option_name.endswith(("time", "timeout")):
            return ConfigType.TIME

        if option_name.endswith(("limit", "count")):
            return ConfigType.NUMBER

        return super().get_config_type(option_name, value)
