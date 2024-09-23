from dataclasses import dataclass
from typing import Optional
from cfgnet.linker.link import Link

@dataclass
class Dependency:
    project: str
    option_name: str
    option_file: str 
    option_value: str
    option_type: str
    option_technology: str
    dependent_option_name: str
    dependent_option_value: str
    dependent_option_type: str
    dependent_option_file: str 
    dependent_option_technology: str


def is_test_file(abs_file_path) -> bool:
    """Check if a given file is a test file."""
    test_indicators = ["/tests", "test", "tests"]
    return any(indicator in abs_file_path for indicator in test_indicators)


def transform(link: Link) -> Dependency:
    """Transform a link into a dependency."""
    dependency = Dependency(
        project=link.artifact_a.parent.name,
        option_name=link.node_a.get_options(),
        option_value=link.node_a.name,
        option_file=link.artifact_a.rel_file_path,
        option_type=link.node_a.config_type,
        option_technology=link.artifact_a.concept_name,
        dependent_option_name=link.node_b.get_options(),
        dependent_option_value=link.node_b.name,
        dependent_option_file=link.artifact_b.rel_file_path,
        dependent_option_type=link.node_b.config_type,
        dependent_option_technology=link.artifact_b.concept_name,
    )

    return dependency