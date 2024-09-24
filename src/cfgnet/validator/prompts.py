from dataclasses import dataclass, field
from llama_index.core import PromptTemplate

@dataclass
class Templates:
    system: PromptTemplate = field(default_factory=PromptTemplate(
        "You are a full-stack expert in validating intra-technology and cross-technology configuration dependencies.\n" 
        "You will be presented with configuration options found in the software project '{project}'.\n\n" 
        "Your task is to determine whether the given configuration options actually depend on each other based on value-equality.\n\n"
        "A value-equality dependency is present if two configuration options must have identical values in order to function correctly.\n"
        "Inconsistencies in these configuration values can lead to configuration errors.\n"
        "Importantly, configuration options may have equal values by accident, meaning that there is no actual dependency, but it just happens that they have equal values.\n"
        "If the values of configuration options are identical merely to ensure consistency within a software project, the options are not considered dependent."
    ))
    task: PromptTemplate = field(default_factory=PromptTemplate(
        "Carefully evaluate whether configuration option {nameA} of type {typeA} with value {valueA} in {fileA} of technology {technologyA} "
        "depends on configuration option {nameB} of type {typeB} with value {valueB} in {fileB} of technology {technologyB} or vice versa." 
    ))
    format: PromptTemplate = field(default_factory=PromptTemplate(
        "Respond in a JSON format as shown below:\n"
        "{{\n"
        "\t“rationale”: string, // Provide a concise explanation of whether and why the configuration options depend on each other due to value-equality.\n"
        "\t“isDependency”: boolean // True if a dependency exists, or False otherwise.\n"
        "}}"
    ))
