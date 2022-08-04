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

import platform
import pathlib
import logging
import os
from typing import Iterable, Set


class IgnoreFile:
    """
    Ignorefile functionality.

    To ignore certain (types of) files or directories for network creation, a
    `.gitignore`-like *ignorefile* can be created at `.cfgnet/ignore`.

    Each line of this *ignorefile* contains a glob-style pattern.  Any files
    that match one or more of these patterns will be ignored by the tool.
    """

    ignored_globs: Set[str] = set()
    system = platform.system()

    @staticmethod
    def configure(ignorefile_path: str):
        IgnoreFile.ignored_globs = set()
        if os.path.exists(ignorefile_path):
            logging.debug("Ignorefile found at %s", ignorefile_path)
            try:
                with open(
                    ignorefile_path, "r", encoding="utf-8"
                ) as ignorefile:
                    IgnoreFile.ignored_globs.update(
                        ignorefile.read().splitlines()
                    )
            except OSError as error:
                logging.error(
                    "Couldn't read ignorefile '%s': %s", ignorefile_path, error
                )

    @staticmethod
    def ignored(file: str) -> bool:
        """Return true iff the file is to be ignored."""
        for glob in IgnoreFile.ignored_globs:
            path = pathlib.PurePath(file)
            # iterate through parents to also match directories
            while str(path) != ".":
                if path.match(glob):
                    return True
                path = path.parent

        return False

    @staticmethod
    def filter(files: Iterable[str]) -> Set[str]:
        return set(file for file in files if not IgnoreFile.ignored(file))
