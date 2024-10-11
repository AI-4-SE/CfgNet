import os
from cfgnet.config_types.config_types import ConfigType
from cfgnet.plugins.file_type.hadoop_plugin import HadoopPlugin


class HadoopHdfsPlugin(HadoopPlugin):
    def __init__(self):
        super().__init__("hadoop-hdfs")

    def is_responsible(self, abs_file_path: str) -> bool:
        file_name = os.path.basename(abs_file_path)
        return any(
            file_name == name for name in ["hdfs-site.xml", "hdfs-default.xml"]
        )

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:

        if option_name.endswith(
            ("name", ".nameservices", ".hostname", ".interfaces")
        ):
            return ConfigType.NAME

        if option_name.endswith((".version")):
            return ConfigType.VERSION_NUMBER

        if option_name.endswith(
            (
                "ms",
                ".seconds",
                ".timeout",
                ".interval",
                ".duration",
                ".lifetime",
                ".millis",
                ".time",
            )
        ):
            return ConfigType.TIME

        if option_name.endswith(
            (
                ".max",
                ".min",
                ".retries",
                ".threshold",
                ".count",
                ".ratio",
                ".threads",
                ".attempts",
                ".volume",
                ".weight",
                ".capacity",
            )
        ):
            return ConfigType.NUMBER

        if option_name.endswith((".url")):
            return ConfigType.URL

        if option_name.endswith(
            (
                ".keystore",
                ".file",
                ".path",
                ".truststore",
                ".dir",
                ".directories",
                ".resource",
                ".volumes",
            )
        ):
            return ConfigType.PATH

        if option_name.endswith((".password")):
            return ConfigType.PASSWORD

        if option_name.endswith((".users", ".username", ".staticuser.user")):
            return ConfigType.USERNAME

        if option_name.endswith((".enabled", ".enable", ".required")):
            return ConfigType.BOOLEAN

        if option_name.endswith(
            (".host", ".http-address", ".http-addresses", "address")
        ):
            return ConfigType.IP_ADDRESS

        if option_name.endswith((".port")):
            return ConfigType.PORT

        if option_name.endswith((".mode")):
            return ConfigType.TYPE

        if option_name.endswith(
            (".buffer", ".blocksize", "size", ".mb", ".bytes")
        ):
            return ConfigType.SIZE

        if option_name.endswith((".id")):
            return ConfigType.ID

        return super().get_config_type(option_name, value)
