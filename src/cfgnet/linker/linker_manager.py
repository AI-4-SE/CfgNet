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

from typing import List, Any

from cfgnet.linker.linker import Linker
from cfgnet.linker.equality_linker import EqualityLinker


class LinkerManager:
    """Manager for linker implementations."""

    all_linker: List[Linker] = [EqualityLinker()]

    @staticmethod
    def apply_linker(network: Any) -> None:
        """
        Apply all existing linker to create links in the configuration network.

        :param: Configuration network
        """
        for linker in LinkerManager.get_all_linker():
            linker.network = network
            linker.create_links()

    @staticmethod
    def get_all_linker():
        """Get all existing linker."""
        return LinkerManager.all_linker
