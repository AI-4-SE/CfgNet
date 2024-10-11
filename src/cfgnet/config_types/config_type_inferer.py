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
from typing import Tuple
from enum import Enum
from cfgnet.config_types.config_types import ConfigType


class Confidence(Enum):
    HIGH = 2
    LOW = 1


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

    regex_port_option = re.compile(r"ports|port|listen|expose")
    regex_port_value = re.compile(
        r"([1-9][0-9]{0,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])"
    )

    regex_size_option = re.compile(r"size|length|memory|byte")
    regex_size_value = re.compile(r"(\d)+ ?(B|KB|MB|GB|TB|PB)")

    regex_username_option = re.compile(r"user|usr|username")
    regex_username_value = re.compile(r"[a-zA-Z][a-zA-Z0-9_]+")

    regex_time_option = re.compile(r"time|timeout|interval|delay|duration")
    regex_time_value = re.compile(r"[\d]+ ?(s|min|h|d|ms)*")

    regex_filepath_option = re.compile(r"path|dir|directory|folder|root")
    regex_filepath_value = re.compile(r"^([~.\w\d]*\/[.\w\d:]+)+(\.[\w\d]+)*$")

    regex_filename_option = re.compile(r"file|filename")
    regex_filename_value = re.compile(
        r"^[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)*\.[a-zA-Z0-9]{1,6}$"
    )

    regex_version_number_option = re.compile(r"version|sdk")
    regex_version_number_value = re.compile(
        r"^(\^|~)?(?:[0-9]{1,3}\.){1,3}[0-9]{1,3}(-[\w]+)?$"
    )

    regex_ip_address_option = re.compile(r"address|ip")
    regex_ip_address_value = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")

    regex_url_option = re.compile(r"url|link")
    regex_url_value = re.compile(r"(https|http)+:\/\/.*")

    regex_email_option = re.compile(r"email|mail")
    regex_email_value = re.compile(r"^(\w)+(\.\w+)*@(\w)+((\.\w+)+)")

    regex_speed_option = re.compile(r"speed|rate")
    regex_speed_value = re.compile(r"[\d]+ ?(bps|Mbps|Kbps)")

    regex_number_value = re.compile(r"[\d.]+")

    regex_id_option = re.compile(r"identifier|id|token")
    regex_id_value = re.compile(r"[a-z0-9-_.]+")

    regex_name_option = re.compile(r"name|alias|label")
    regex_name_value = re.compile(r"^[a-zA-Z0-9_\-.]+$")

    regex_image_option = re.compile(r"image|from")
    regex_command_option = re.compile(
        r"command|entrypoint|cmd|script|bin|install|run|exec"
    )
    regex_command_value = re.compile(r"^[\/ a-zA-Z_\-.$]+$")
    regex_license_option = re.compile(r"license|licence")
    regex_type_option = re.compile(r"packaging|format|type")
    regex_platform_option = re.compile(r"platform|system")
    regex_boolean_option = re.compile(
        r"allow|inactive|enable|disable|flag|switch|active"
    )

    def is_number(self, value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False

    def is_boolean(self, value: str) -> bool:
        return value.lower() in [
            "true",
            "false",
            "1",
            "0",
            "yes",
            "no",
            "on",
            "off",
        ]

    def is_bool(self, option_name: str, value: str) -> Tuple:
        if re.search(
            self.regex_boolean_option, option_name
        ) and value.lower() in [
            "true",
            "false",
            "1",
            "0",
            "yes",
            "no",
            "on",
            "off",
        ]:
            return True, Confidence.HIGH
        return False, None

    def is_username(self, option_name: str, value: str) -> Tuple:
        if re.search(self.regex_username_option, option_name) and re.fullmatch(
            self.regex_username_value, value
        ):
            return True, Confidence.HIGH

        if re.search(self.regex_username_option, option_name):
            return True, Confidence.LOW

        return False, None

    def is_port(self, option_name: str, value: str) -> Tuple:
        try:
            port_value = int(value)
            is_port_value = 0 <= port_value <= 665535
            if is_port_value and re.search(
                self.regex_port_option, option_name
            ):
                return True, Confidence.HIGH

            if (
                re.search(self.regex_port_option, option_name)
                and not is_port_value
            ):
                return True, Confidence.LOW

            return False, None
        except ValueError:
            return False, None

    def is_size(self, option_name: str, value: str) -> Tuple:
        if re.search(self.regex_size_option, option_name) and re.fullmatch(
            self.regex_size_value, value
        ):
            return True, Confidence.HIGH

        if re.search(self.regex_size_option, option_name) and self.is_number(
            value
        ):
            return True, Confidence.HIGH

        if re.fullmatch(self.regex_size_value, value) or re.search(
            self.regex_size_option, option_name
        ):
            return True, Confidence.LOW

        return False, None

    def is_time(self, option_name: str, value: str) -> Tuple:
        if re.search(self.regex_time_option, option_name) and re.fullmatch(
            self.regex_time_value, value
        ):
            return True, Confidence.HIGH

        if re.search(self.regex_time_option, option_name) and self.is_number(
            value
        ):
            return True, Confidence.HIGH

        if re.search(self.regex_time_option, option_name):
            return True, Confidence.LOW

        return False, None

    def is_password(self, option_name: str, value: str) -> Tuple:
        if re.search(self.regex_password_option, option_name) and re.fullmatch(
            self.regex_password_value, value
        ):
            return True, Confidence.HIGH

        if re.search(self.regex_password_option, option_name):
            return True, Confidence.LOW

        return False, None

    def is_path(self, option_name: str, value: str) -> Tuple:
        if re.search(self.regex_filepath_option, option_name) and re.fullmatch(
            self.regex_filepath_value, value
        ):
            return True, Confidence.HIGH

        if re.search(self.regex_filepath_option, option_name) or re.fullmatch(
            self.regex_filepath_value, value
        ):
            return True, Confidence.LOW

        return False, None

    def is_filename(self, option_name: str, value: str) -> Tuple:
        if re.search(self.regex_filename_option, option_name) and re.fullmatch(
            self.regex_filename_value, value
        ):
            return True, Confidence.HIGH

        if re.fullmatch(self.regex_filename_value, value):
            return True, Confidence.LOW

        return False, None

    def is_version_number(self, option_name: str, value: str) -> Tuple:
        if re.search(
            self.regex_version_number_option, option_name
        ) and re.fullmatch(self.regex_version_number_value, value):
            return True, Confidence.HIGH

        if re.search(self.regex_version_number_option, option_name):
            return True, Confidence.LOW

        return False, None

    def is_ip_address(self, option_name: str, value: str) -> Tuple:
        if re.search(
            self.regex_ip_address_option, option_name
        ) and re.fullmatch(self.regex_ip_address_value, value):
            return True, Confidence.HIGH

        if re.fullmatch(self.regex_ip_address_value, value):
            return True, Confidence.LOW

        return False, None

    def is_email(self, option_name: str, value: str) -> Tuple:
        if re.search(self.regex_email_option, option_name) and re.fullmatch(
            self.regex_email_value, value
        ):
            return True, Confidence.HIGH

        if re.fullmatch(self.regex_email_value, value) or re.search(
            self.regex_email_option, option_name
        ):
            return True, Confidence.LOW

        return False, None

    def is_speed(self, option_name: str, value: str) -> Tuple:
        if re.search(self.regex_speed_option, option_name) and re.fullmatch(
            self.regex_speed_value, value
        ):
            return True, Confidence.HIGH

        if re.search(self.regex_speed_option, option_name) and self.is_number(
            value
        ):
            return True, Confidence.HIGH

        if re.fullmatch(self.regex_speed_value, value) or re.search(
            self.regex_speed_option, option_name
        ):
            return True, Confidence.LOW

        return False, None

    def is_url(self, option_name: str, value: str) -> Tuple:
        if re.search(self.regex_url_option, option_name) and re.fullmatch(
            self.regex_url_value, value
        ):
            return True, Confidence.HIGH

        if re.fullmatch(self.regex_url_value, value) or re.search(
            self.regex_url_option, option_name
        ):
            return True, Confidence.LOW

        return False, None

    def is_id(self, option_name: str, value: str) -> Tuple:
        if re.search(self.regex_id_option, option_name) and re.fullmatch(
            self.regex_id_value, value
        ):
            return True, Confidence.HIGH

        if re.search(self.regex_id_option, option_name):
            return True, Confidence.LOW

        return False, None

    # pylint: disable=unused-argument
    def is_image(self, option_name: str, value: str) -> Tuple:
        if re.search(self.regex_image_option, option_name):
            return True, Confidence.LOW

        return False, None

    def is_command(self, option_name: str, value: str) -> Tuple:
        if re.search(self.regex_command_option, option_name) and re.fullmatch(
            self.regex_command_value, value
        ):
            return True, Confidence.HIGH

        if re.search(self.regex_command_option, option_name):
            return True, Confidence.LOW

        return False, None

    # pylint: disable=unused-argument
    def is_license(self, option_name: str, value: str) -> Tuple:
        if re.search(self.regex_license_option, option_name):
            return True, Confidence.LOW

        return False, None

    def is_name(self, option_name: str, value: str) -> Tuple:
        if re.search(self.regex_name_option, option_name) and re.fullmatch(
            self.regex_name_value, value
        ):
            return True, Confidence.LOW

        if re.search(self.regex_name_option, option_name):
            return True, Confidence.LOW

        return False, None

    # pylint: disable=unused-argument
    def is_type(self, option_name: str, value: str) -> Tuple:
        if re.search(self.regex_type_option, option_name):
            return True, Confidence.LOW

        return False, None

    # pylint: disable=unused-argument
    def is_platform(self, option_name: str, value: str) -> Tuple:
        if re.search(self.regex_platform_option, option_name):
            return True, Confidence.LOW

        return False, None

    def get_config_type(self, option_name: str, value: str):
        """
        Get config type based on naming conventions and syntax patterns.

        :param option_name: name of option
        :param value: value of option
        :return: return configuration type
        """
        results = []

        # Check for each type using respective methods and append to results
        checks = [
            (self.is_password, ConfigType.PASSWORD),
            (self.is_port, ConfigType.PORT),
            (self.is_size, ConfigType.SIZE),
            (self.is_username, ConfigType.USERNAME),
            (self.is_time, ConfigType.TIME),
            (self.is_path, ConfigType.PATH),
            (self.is_version_number, ConfigType.VERSION_NUMBER),
            (self.is_ip_address, ConfigType.IP_ADDRESS),
            (self.is_email, ConfigType.EMAIL),
            (self.is_speed, ConfigType.SPEED),
            (self.is_url, ConfigType.URL),
            (self.is_id, ConfigType.ID),
            (self.is_image, ConfigType.IMAGE),
            (self.is_command, ConfigType.COMMAND),
            (self.is_license, ConfigType.LICENSE),
            (self.is_name, ConfigType.NAME),
            (self.is_type, ConfigType.TYPE),
            (self.is_platform, ConfigType.PLATFORM),
            (self.is_filename, ConfigType.PATH),
            (self.is_bool, ConfigType.BOOLEAN),
        ]

        option_name = option_name.lower()

        for check_method, config_type in checks:
            matched, confidence = check_method(option_name, value)
            if matched:
                results.append((config_type, confidence))

        results.sort(key=lambda x: x[1].value, reverse=True)

        print(results)
        print(option_name, value)

        if self.is_boolean(value):
            return ConfigType.BOOLEAN

        if results:
            if len(results) == 1:
                return results[0][0]

            if len(results) > 1:
                confidence_levels = [result[1] for result in results][:2]

                print(len(confidence_levels))

                if all(
                    confidence == confidence_levels[0]
                    for confidence in confidence_levels
                ):
                    return ConfigType.UNKNOWN

                return results[0][0]

        if self.is_number(value):
            return ConfigType.NUMBER

        return ConfigType.UNKNOWN
