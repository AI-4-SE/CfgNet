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
    SPEED = auto()
    SIZE = auto()
    IP_ADDRESS = auto()
    ID = auto()

    # Strings
    NAME = auto()
    USERNAME = auto()
    PASSWORD = auto()
    URL = auto()
    EMAIL = auto()
    IMAGE = auto()
    PATH = auto()
    COMMAND = auto()
    LICENSE = auto()
    ENVIRONMENT = auto()
    PLATFORM = auto()
    TYPE = auto()

    BOOLEAN = auto()
    NUMBER = auto()
    UNKNOWN = auto()
