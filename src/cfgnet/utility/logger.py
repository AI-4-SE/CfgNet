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

import logging
import os

# basic logging formatter
log_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)8s | %(module)20s | %(message)s",
)


logging.root.setLevel(logging.NOTSET)


def configure_console_logger(verbose: bool):
    """Configure console logger."""
    console_logging_handler = logging.StreamHandler()
    console_logging_handler.setFormatter(log_formatter)

    if verbose:
        console_logging_handler.setLevel(logging.DEBUG)
        console_logging_handler.addFilter(LogFileFilter())
    else:
        console_logging_handler.setLevel(logging.INFO)
        console_logging_handler.addFilter(ConsoleFilter())

    logging.getLogger().addHandler(console_logging_handler)


def configure_repo_logger(repo_log_file_path: str):
    """Configure logging to per-repo logfile."""
    log_dir = os.path.dirname(repo_log_file_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    repo_logging_handler = logging.FileHandler(repo_log_file_path)
    repo_logging_handler.setLevel(logging.DEBUG)
    repo_logging_handler.setFormatter(log_formatter)
    repo_logging_handler.addFilter(LogFileFilter())
    logging.getLogger().addHandler(repo_logging_handler)


class LogFileFilter(logging.Filter):
    """Logging filter to suppress logs fired by module 'cmd'."""

    def filter(self, record: logging.LogRecord) -> bool:
        return record.module != "cmd"


class ConsoleFilter(logging.Filter):
    """Logging filter for the console."""

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno in (logging.INFO, logging.ERROR)
