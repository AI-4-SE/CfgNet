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
from enum import Enum, auto


class ConfigType(Enum):
    # Numbers
    TIME = auto()
    PORT = auto()
    VERSION_NUMBER = auto()
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
    HOST = auto()
    STATE = auto()

    # Booleans
    BOOLEAN = auto()
    MODE = auto()

    # UNKNOWN
    UNKNOWN = auto()
