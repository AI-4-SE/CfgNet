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
import re
from cfgnet.config_types.config_types import ConfigType


# pylint: disable=too-many-public-methods
class ConfigTypeInferer:
    """
    The ConfigTypeInferer infers types based on regular expressions.

    The regular expression stem from several research papers:
    - Correlation Explorer, EnCore, COnfTest, ConfVD

    Inferring a config type follows several rules:

    1. First, the option name and value are checked against types for which
    an option name and value regex exists.
    2. Second, the option name or value are checked against specific types
    for which exist only one regular expression.
    3. Lastly, the option name or value checked against general types.
    """

    regex_password_option = re.compile(r"password|pwd|pass")
    regex_password_value = re.compile(r".+")
    regex_port_option = re.compile(r"port|listen|expose|in|out")
    regex_port_value = re.compile(
        r"([1-9][0-9]{0,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])"
    )
    regex_size_option = re.compile(
        r"size|length|max|min|threshold|weight|height|memory|mem"
    )
    regex_size_value = re.compile(r"(\d)+ ?(B|KB|MB|GB|TB|PB)+")
    regex_username_option = re.compile(r"user|usr|username")
    regex_username_value = re.compile(r"[a-zA-Z][a-zA-Z0-9_]+")
    regex_time_option = re.compile(
        r"time|interval|day|month|year|hour|minute|second|millisecond"
    )
    regex_time_value = re.compile(r"[\d]+ ?(s|min|h|d|ms)*")
    regex_filepath_option = re.compile(
        r"file|path|dir|directory|folder|destination"
    )
    # regex_filepath_value = re.compile(r"\/?([^\/]+\/)+[^\/]*")
    regex_filepath_value = re.compile(r"^([~.\w\d]*\/[.\w\d]+)+(\.[\w\d]+)*$")
    regex_version_number_option = re.compile(r"version|target|source")
    regex_version_number_value = re.compile(
        r"^(\^|~)?(?:[0-9]{1,3}\.){2}[0-9]{1,3}(-[\w]+)?$"
    )
    regex_ip_address_option = re.compile(r"address|ip")
    regex_ip_address_value = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")

    regex_domain_main = re.compile(
        r"(telnet|https|http|ftp)+:\/\/(\w)+((\.\w+)+):[\d]+"
    )
    regex_url = re.compile(r"(https|http)+:\/\/.*")
    regex_boolean = re.compile(
        r"[tT][rR][uU][eE]|[fF][aA][lL][sS][eE]|[oO][nN]|[oO][fF]{2}|[yY][eE][sS]|[nN][oO]"
    )
    regex_filename = re.compile(r"\/?[a-zA-z_-]+\.[a-zA-z_-]+")
    regex_email = re.compile(r"^(\w)+(\.\w+)*@(\w)+((\.\w+)+)")
    regex_speed = re.compile(r"[\d]+ ?(bps|Mbps|Kbps)")
    regex_number = re.compile(r"[\d.]+")
    regex_id = re.compile(r"identity|identifier|id")
    regex_name = re.compile(r"name|alias")
    regex_mode = re.compile(r"mode")
    regex_count = re.compile(r"count")
    regex_pattern = re.compile(r"match|pattern")
    regex_environment = re.compile(r"env|environment")
    regex_image = re.compile(r"image")
    regex_command = re.compile(r"command|entrypoint|cmd|script|bin|install")
    regex_license = re.compile(r"license")

    @staticmethod
    def is_boolean(value: str) -> bool:
        return bool(re.match(ConfigTypeInferer.regex_boolean, value))

    # pylint: disable=too-many-return-statements
    @staticmethod
    def get_config_type(  # noqa: C901
        option_name: str, value: str
    ) -> ConfigType:
        """Check the option value and return its config type."""
        # Check option name and value against types for which an option name and value regex exists.
        if bool(
            re.match(ConfigTypeInferer.regex_port_option, option_name)
        ) and bool(re.fullmatch(ConfigTypeInferer.regex_port_value, value)):
            return ConfigType.PORT

        if bool(
            re.match(ConfigTypeInferer.regex_username_option, option_name)
        ) and bool(
            re.fullmatch(ConfigTypeInferer.regex_username_value, value)
        ):
            return ConfigType.USERNAME

        if bool(
            re.search(ConfigTypeInferer.regex_size_option, option_name)
        ) and bool(re.fullmatch(ConfigTypeInferer.regex_size_value, value)):
            return ConfigType.SIZE

        if bool(
            re.search(ConfigTypeInferer.regex_time_option, option_name)
        ) and bool(re.fullmatch(ConfigTypeInferer.regex_time_value, value)):
            return ConfigType.TIME

        if bool(
            re.match(ConfigTypeInferer.regex_password_option, option_name)
        ) and bool(
            re.fullmatch(ConfigTypeInferer.regex_password_value, value)
        ):
            return ConfigType.PASSWORD

        if bool(
            re.search(ConfigTypeInferer.regex_filepath_option, option_name)
        ) or bool(re.fullmatch(ConfigTypeInferer.regex_filepath_value, value)):
            return ConfigType.PATH

        if bool(
            re.search(
                ConfigTypeInferer.regex_version_number_option, option_name
            )
        ) or bool(
            re.fullmatch(ConfigTypeInferer.regex_version_number_value, value)
        ):
            return ConfigType.VERSION_NUMBER

        if bool(
            re.search(ConfigTypeInferer.regex_ip_address_option, option_name)
        ) or bool(
            re.fullmatch(ConfigTypeInferer.regex_ip_address_value, value)
        ):
            return ConfigType.IP_ADDRESS

        # Check option name and value against specific types.
        if bool(re.fullmatch(ConfigTypeInferer.regex_filename, value)):
            return ConfigType.PATH

        if bool(re.fullmatch(ConfigTypeInferer.regex_email, value)):
            return ConfigType.EMAIL

        if bool(re.fullmatch(ConfigTypeInferer.regex_domain_main, value)):
            return ConfigType.DOMAIN_NAME

        if bool(re.fullmatch(ConfigTypeInferer.regex_speed, value)):
            return ConfigType.SPEED

        if bool(re.fullmatch(ConfigTypeInferer.regex_url, value)):
            return ConfigType.URL

        if bool(re.search(ConfigTypeInferer.regex_id, option_name)):
            return ConfigType.ID

        if bool(re.search(ConfigTypeInferer.regex_mode, option_name)):
            return ConfigType.MODE

        if bool(re.search(ConfigTypeInferer.regex_count, option_name)):
            return ConfigType.COUNT

        if bool(re.search(ConfigTypeInferer.regex_name, option_name)):
            return ConfigType.NAME

        if bool(re.search(ConfigTypeInferer.regex_pattern, option_name)):
            return ConfigType.PATTERN

        if bool(re.search(ConfigTypeInferer.regex_environment, option_name)):
            return ConfigType.ENVIRONMENT

        if bool(re.search(ConfigTypeInferer.regex_image, option_name)):
            return ConfigType.IMAGE

        if bool(re.search(ConfigTypeInferer.regex_command, option_name)):
            return ConfigType.COMMAND

        if bool(re.search(ConfigTypeInferer.regex_license, option_name)):
            return ConfigType.LICENSE

        # Check option name and value against general types.
        if bool(re.fullmatch(ConfigTypeInferer.regex_number, value)):
            return ConfigType.NUMBER

        if bool(re.fullmatch(ConfigTypeInferer.regex_boolean, value)):
            return ConfigType.BOOLEAN

        if bool(re.fullmatch(ConfigTypeInferer.regex_size_value, value)):
            return ConfigType.SIZE

        return ConfigType.UNKNOWN
