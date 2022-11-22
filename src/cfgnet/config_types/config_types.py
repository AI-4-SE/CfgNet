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
from enum import Enum, auto


class ConfigType(Enum):
    # Numbers
    TIME = auto()
    PORT = auto()
    VERSION_NUMBER = auto()
    MEMORY = auto()
    FRACTION = auto()
    SPEED = auto()
    PERMISSION = auto()
    COUNT = auto()
    SIZE = auto()
    IP_ADDRESS = auto()
    NUMBER = auto()
    ID = auto()

    # Strings
    NAME = auto()
    USERNAME = auto()
    PASSWORD = auto()
    URL = auto()
    EMAIL = auto()
    DOMAIN_NAME = auto()
    PROTOCOL = auto()
    IMAGE = auto()
    PATH = auto()
    COMMAND = auto()
    LICENSE = auto()
    ENVIRONMENT = auto()
    PATTERN = auto()
    PLATFORM = auto()
    LANGUAGE = auto()
    TYPE = auto()
    MIME = auto()

    # Booleans
    BOOLEAN = auto()
    MODE = auto()

    # UNKNOWN
    UNKNOWN = auto()

    @staticmethod
    def is_filepath(value: str) -> bool:
        """Check if value is a file path."""
        return bool(re.match(r"[\/\w.-]*(\/+[\w.-]+)+\/?", value))

    @staticmethod
    def is_java_executable(value: str) -> bool:
        return bool(re.match(r"((\/)*[\w.-]+)+\/?(.jar|.war)", value))

    @staticmethod
    def is_domain_name(value: str) -> bool:
        """Check if value is a domain name."""
        return bool(re.match(r"(https|http)?:\/\/[a-zA-Z0-9.]+", value))

    @staticmethod
    def is_boolean(value: str) -> bool:
        """Check if value is a boolean."""
        return bool(re.match(r"(on|off|yes|no|true|false)", value.lower()))

    @staticmethod
    def is_ip_address(value: str) -> bool:
        """Check if value is an ip address."""
        return bool(
            re.match(
                r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$", value
            )
        )

    @staticmethod
    def is_email(value: str) -> bool:
        """Check if value is an email."""
        return bool(re.match(r"^\S+@\S+\.\S+$", value))

    @staticmethod
    def is_port(value: str) -> bool:
        """Check if value is a port."""
        try:
            port = int(value)
            return 0 <= port <= 65535
        except ValueError:
            return False

    @staticmethod
    def is_version_number(value: str) -> bool:
        """Check if value is a version number."""
        return bool(re.match(r"^(\d+\.)?(\d+\.)?(\*|\d+(\-\w+)?)$", value))

    # pylint: disable=too-many-return-statements
    @staticmethod
    def get_config_type(value: str) -> "ConfigType":
        """Return the config type of the value."""
        if ConfigType.is_filepath(value):
            return ConfigType.PATH
        if ConfigType.is_boolean(value):
            return ConfigType.BOOLEAN
        if ConfigType.is_domain_name(value):
            return ConfigType.DOMAIN_NAME
        if ConfigType.is_email(value):
            return ConfigType.EMAIL
        if ConfigType.is_ip_address(value):
            return ConfigType.IP_ADDRESS
        if ConfigType.is_port(value):
            return ConfigType.PORT
        if ConfigType.is_version_number(value):
            return ConfigType.VERSION_NUMBER
        if ConfigType.is_java_executable(value):
            return ConfigType.PATH
        return ConfigType.UNKNOWN
