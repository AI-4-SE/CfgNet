import os
import platform
import logging
from typing import Set, Optional


def is_in_excluded_directory(file_path) -> bool:
    """Check if a given file is in an excluded directory."""
    # Normalize and split the file path
    normalized_path = os.path.normpath(file_path)
    directories = normalized_path.split(os.sep)

    # List of excluded directory names
    excluded_dirs = {
        "docs", 
        "data", 
        "lib", 
        "benchmark",
        "benchmarks", 
        "annotations", 
        "examples", 
        "spec",
        "specs",
        "fonts",
        "videos",
        "images",
        "audios",
        "cache"
    }

    # Check if any directory in the path matches excluded directories
    for dir_name in directories:
        dir_lower = dir_name.lower()
        # Check for exact match or if 'test' is in the directory name
        if dir_lower in excluded_dirs or "test" in dir_lower:
            return True
    return False


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
