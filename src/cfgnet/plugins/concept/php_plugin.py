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
from typing import List
from cfgnet.config_types.config_types import ConfigType
from cfgnet.plugins.file_type.configparser_plugin import ConfigParserPlugin


class PhpPlugin(ConfigParserPlugin):
    def __init__(self):
        super().__init__("php")
        self.excluded_keys: List[str] = ["extension"]

    def is_responsible(self, abs_file_path) -> bool:
        if abs_file_path.endswith("php.ini"):
            return True
        return False

    # pylint: disable=unused-argument,too-many-return-statements
    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        option_name = option_name.lower()

        if option_name.endswith(("default_pw")):
            return ConfigType.USERNAME

        if option_name in (
            "instance_name",
            "default_db",
            "name",
            "user_agent",
            "timezone",
            "default_db",
            "default_charset",
            "default_socket",
            "default_host",
            "SMTP",
        ):
            return ConfigType.NAME

        if option_name.endswith(("format", "http_output_conv_mimetypes")):
            return ConfigType.TYPE

        if option_name.endswith(
            (
                "max_len",
                "precision",
                "file_uploads",
                "number",
            )
        ):
            return ConfigType.NUMBER

        if option_name in (
            "memory_limit",
            "memory_consumption",
            "interned_strings_buffer",
            "max_file_size",
            "wsdl_cache_limit",
            "max_persistent",
            "max_links",
            "max_accelerated_files",
            "regex_retry_limit",
            "regex_stack_limit",
            "max_failover_attempts",
            "default_prefetch",
            "jit_blacklist_root_trace",
            "jit_blacklist_side_trace",
            "jit_max_loop_unrolls",
            "jit_max_recursive_calls",
            "jit_max_recursive_returns",
            "jit_max_polymorphic_calls",
            "backtrack_limit",
            "recursion_limit",
            "sid_length",
        ):
            return ConfigType.SIZE

        if option_name.endswith(("size", "match_max")):
            return ConfigType.SIZE

        if option_name.endswith(("cache_ttl", "timeout")):
            return ConfigType.TIME

        if option_name in (
            "ping_interval",
            "cookie_lifetime",
            "cache_expire",
            "upload_progress.min_freq",
        ):
            return ConfigType.TIME

        if option_name in ("default_mimetype"):
            return ConfigType.TYPE

        return super().get_config_type(option_name, value)
