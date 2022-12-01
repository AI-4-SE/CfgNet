# This file is part of the CfgNet module.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <https://www.gnu.org/licenses/>.

from cfgnet.plugins.file_type.configparser_plugin import ConfigParserPlugin
from cfgnet.config_types.config_types import ConfigType


class MysqlPlugin(ConfigParserPlugin):
    def __init__(self):
        super().__init__("mysql")

    def is_responsible(self, abs_file_path) -> bool:
        if abs_file_path.endswith(("my.cnf", "my.ini")):
            return True
        return False

    # pylint: disable=unused-argument,too-many-return-statements
    def get_config_type(self, option_name: str) -> ConfigType:  # noqa: C901
        """
        Find config type based on option name.

        Option types included from:
        https://dev.mysql.com/doc/refman/8.0/en/server-system-variables.html

        :param option_name: name of option
        :return: config type
        """
        option_name = option_name.lower()
        if option_name.endswith(("dir", "file", "directory", "path")):
            if not option_name == "core_file":
                return ConfigType.PATH

        if option_name in (
            "admin_ssl_ca",
            "admin_ssl_cert",
            "admin_ssl_crl",
            "admin_ssl_key",
            "log_error",
            "secure_file_priv",
            "socket",
            "ssl_ca",
            "ssl_cert",
            "ssl_crl",
            "ssl_key",
        ):
            return ConfigType.PATH

        if option_name in ("port"):
            return ConfigType.PORT

        if option_name == "password":
            return ConfigType.PASSWORD

        if option_name in ("user", "external_user", "proxy_user"):
            return ConfigType.USERNAME

        if option_name in ("admin_address", "bind_address"):
            return ConfigType.IP_ADDRESS

        if option_name.endswith(("version", "version_compile_zlib")):
            return ConfigType.VERSION_NUMBER

        if option_name in (
            "thread_pool_query_threads_per_group",
            "temptable_max_mmap",
            "back_log",
            "caching_sha2_password_digest_rounds",
            "default_week_format",
            "div_precision_increment",
            "ft_max_word_len",
            "information_schema_stats_expiry",
            "log_throttle_queries_not_using_indexes",
            "max_connect_errors",
            "max_length_for_sort_data",
            "max_points_in_geometry",
            "password_history",
            "password_reuse_interval",
            "rand_seed1",
            "rand_seed2",
        ):
            return ConfigType.NUMBER

        if option_name.endswith(
            (
                "max_len",
                "min_len",
                "length",
                "threshold",
                "threads",
                "count",
                "depth",
                "connections",
                "offset",
                "instances",
            )
        ):
            return ConfigType.NUMBER

        if option_name.endswith("mode"):
            return ConfigType.MODE

        if option_name.endswith(
            (
                "size",
                "limit",
                "cache",
                "max_allowed_packet",
                "max_ram",
                "thread_stack",
            )
        ):
            return ConfigType.SIZE

        if option_name in (
            "use_secondary_engine",
            "transaction_isolation",
            "thread_handling",
            "completion_type",
            "concurrent_insert",
            "default_authentication_plugin",
            "default_collation_for_utf8mb4",
            "delay_key_write",
            "event_scheduler",
            "authentication_windows_log_level",
            "internal_tmp_disk_storage_engine",
            "internal_tmp_mem_storage_engine",
            "log_error_verbosity",
            "myisam_recover_options",
            "myisam_stats_method",
            "offline_mode",
            "optimizer_prune_level",
            "protocol_compression_algorithms",
            "rbr_exec_mode",
            "session_track_gtids",
            "sql_mode",
            "ssl_fips_mode",
            "ssl_session_cache_mode",
        ):
            return ConfigType.MODE

        if option_name.endswith(
            ("timeout", "time", "delay", "timer", "timestamp")
        ):
            return ConfigType.TIME

        if option_name in ("ft_boolean_syntax"):
            return ConfigType.PATTERN

        if option_name in ("hostname", "shared_memory_base_name"):
            return ConfigType.NAME

        if option_name in ("license"):
            return ConfigType.LICENSE

        if option_name.endswith(("pseudo_thread_id", "_id")):
            return ConfigType.ID

        if option_name in ("version_compile_os"):
            return ConfigType.PLATFORM

        return ConfigType.UNKNOWN
