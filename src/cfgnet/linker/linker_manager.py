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

from typing import List, TYPE_CHECKING

from cfgnet.linker.linker import Linker
from cfgnet.linker.equality_linker import EqualityLinker

if TYPE_CHECKING:
    from cfgnet.network.network import Network


class LinkerManager:
    """Manager for linker implementations."""

    all_linkers: List[Linker] = [EqualityLinker()]

    @staticmethod
    def apply_linkers(network: "Network") -> None:
        """
        Apply all existing linker to create links in the configuration network.

        :param: Configuration network
        """
        for linker in LinkerManager.all_linkers:
            linker.network = network
            linker.create_links()
