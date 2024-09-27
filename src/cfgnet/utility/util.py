import os
import platform
import logging
from typing import Set, Optional


def is_test_file(abs_file_path) -> bool:
    """
    Check if a given file is a test file.

    :return: True if test file else False
    """
    test_indicators = ["/tests", "test", "tests"]
    return any(indicator in abs_file_path for indicator in test_indicators)


def get_system_config_dir() -> Optional[str]:
    """
    Determine the system configuration directory based on the operating system.

    :return: Path to the system configuration directory
    """
    os_type = platform.system()

    print("OS: ", os_type)

    if os_type == "Linux":
        # Common Linux config directories
        return "/etc"

    if os_type == "Windows":
        # Windows config directory (use environment variables for system paths)
        return os.getenv("ProgramData", "C:\\ProgramData")

    logging.error("System config directory not defined for OS %s. ", os_type)
    return None


def get_system_files() -> Set:
    config_dir = get_system_config_dir()
    system_files = set()

    if config_dir:
        for root, _, files in os.walk(config_dir):
            for file in files:
                print("File: ", file)
                abs_file_path = os.path.join(root, file)
                system_files.add(abs_file_path)

    return system_files
