![](https://github.com/AI-4-SE/CfgNet/workflows/Tests/badge.svg?branch=main)
![](https://github.com/AI-4-SE/CfgNet/workflows/Code%20Style/badge.svg?branch=main)

# CfgNet

CfgNet is a plugin-based framework for detecting and tracking dependencies among configuration options across the used technology stack of a software project.
Essentially, CfgNet represents configuration options of configuration artifacts as trees and connects them to build a configuration network, where links between the leaf nodes of a tree correspond to the dependencies between configuration options.
Our idea is to have a framework in which technology plugins analyze different configuration files (e.g., Dockerfiles or build scripts) and create nodes for configuration options with their user-defined values.
Linker plugins then connect the nodes in case a dependency exists using a specific linker heuristic.

We envision that CfgNet is used within a Git hook (e.g., pre-commit hook) to prevent dependency conflicts during the development and maintenance of software systems. 
That is, whenever changes are made, CfgNet can check the changes before the actual commit gets pushed to the repository and reports a warning if it has detected possible dependency conflicts. 
This way, developer can check the changes again and even use the information that CfgNet provides to fix the dependency conflicts.

## Installation

CfgNet is a package on PyPI. You can install it with the following command:

    pip install cfgnet

You can also build it locally with [poetry](https://python-poetry.org/).
Please refer to the documentation of poetry for further details.

## Basic Usage

CfgNet provides a method-based command line interface with the commands `init`, `validate`, `export`, `analyze`, and `extract`.
Each method requires the `project_root` as option that points towards the root directory of the project on which you want to apply the CfgNet.

To initialize a reference configuration network, use the `init` command.

    cfgnet init <project_root>


To detect dependency conflicts against the initialized reference network, you need to call
the `validate` command. Detected dependency conflicts will be displayed on screen.

    cfgnet validate <project_root>


To export the reference network for visualization, use the `export` command.
The `export` command additionally requires a `output` and `format` option.
While the former specifies the name of the output file the latter defines which format the configuration network should be converted to.
Available formats are `json` and `dot`.
By default, the export includes only linked value nodes.
To export all nodes from the configuration network, you have te set the option `include-unlinked`. 

    cfgnet export --output=<name> --format=<format> <project_root>
    cfgnet export --output=<name> --format=<format> --include-unlinked <project_root>

To visualize the reference network immediately without exporting the format, use the `export` command with the `-visualize-dot` option. 
The visualization of the configuration network is stored in `.cfgnet/export` using the `png` format by default.
However, the format can be changed to either `pdf` or `png` using the format option.
By default, the network visualization includes only linked value nodes.
To visualize the entire configuration network including value nodes that are not linked to other nodes, you have to set the option `include-unlinked`. 

    cfgnet export --output=<name> --visualize-dot <project_root>
    cfgnet export --output=<name> --format=<format> --visualize-dot <project_root>
    cfgnet export --output=<name> --format=<format> --include-unlinked --visualize-dot <project_root>

The `analyze` command is used for analyzing the commit history of software systems in an automated manner.
When the analysis is finished, all detected configuration conflicts will be stored in `.cfgnet/analysis`.

    cfgnet analyze <project_root>

To extract the key-value pairs of all configuration artifacts within a software project, use the `extract` command. The `extract` command additionally requires an `output` options, which specifies the directory where the key-value pairs are stored using the JSON format. 

    cfgnet extract <project_root> --output=<output>

The commands `init` and `analyze` can be further configured with the following options:
    
    (1) --enable-static-blacklist
    (2) --enable-internal-conflicts
    (3) --enable-all-conflicts
    (4) --config-files=<absolute_file_path>

These options enable (1) blacklisted values, which are taken into account when creating links, (2) the detection of conflicts within the same configuration artifact, (3) the detection of all conflict types, and (4) parsing of specific configuration files (e.g., configuration files of the operating machine that are not in the git repository of the software project), respectively. The option `--config-files` can be specified multiple times. The `config-file` option can also be used to configure the `extract` command.

For a documentation of further options run

    cfgnet --help

## Documentation

You can build the documentation with

    make docs

The HTML version of the documentation will be in `docs/_build/html`.

## Contributing

To contribute to this project feel free to create pull requests.
Please read our [guidelines and instructions for development][development] first.

[releases]: https://github.com/AI-4-SE/CfgNet/releases
[development]: docs/development.rst
