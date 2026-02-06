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
import os
import logging
import configparser
import re
from typing import Optional, Dict

from groovy_parser.parser import parse_groovy_content

from cfgnet.config_types.config_types import ConfigType
from cfgnet.network.nodes import ArtifactNode, OptionNode, ValueNode, ProjectNode
from cfgnet.plugins.plugin import Plugin


class GradlePlugin(Plugin):
    def __init__(self):
        super().__init__("gradle")

    def is_responsible(self, abs_file_path):
        file_name = os.path.basename(abs_file_path)
        return file_name in ["gradle.properties", "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"]

    def _parse_config_file(
        self,
        abs_file_path: str,
        rel_file_path: str,
        root: Optional[ProjectNode],
    ) -> ArtifactNode:
        file_name = os.path.basename(abs_file_path)

        if file_name == "gradle.properties":
            return self._parse_properties_file(abs_file_path, rel_file_path, root)
        else:
            return self._parse_gradle_build_file(abs_file_path, rel_file_path, root)

    def _parse_properties_file(
        self,
        abs_file_path: str,
        rel_file_path: str,
        root: Optional[ProjectNode],
    ) -> ArtifactNode:
        """Parse gradle.properties files using ConfigParser."""
        artifact = ArtifactNode(
            file_path=abs_file_path,
            rel_file_path=rel_file_path,
            concept_name=self.concept_name,
            project_root=root,
        )

        with open(abs_file_path, "r", encoding="utf-8") as file:
            line_dict = {}
            lineno = 1
            for line in file:
                line = line.strip()
                if len(line) > 0:
                    line_dict[line] = lineno
                lineno += 1

        with open(abs_file_path, "r", encoding="utf-8") as config_file:
            file_content = config_file.read()

        try:
            dummy_section = "[dummy_section]\n"
            config = configparser.ConfigParser(
                interpolation=None, allow_no_value=True
            )
            config.read_string(dummy_section + file_content)
        except (AttributeError, configparser.Error) as error:
            logging.warning(
                'Failed to parse properties file "%s" with configparser due to "%s"',
                rel_file_path,
                str(error),
            )
            return artifact

        for section_name in config:
            if section_name == "DEFAULT":
                continue

            section = config[section_name]

            if len(section.keys()) == 0:
                continue

            parent = artifact

            for option in section.keys():
                config_type = self.get_config_type(option_name=option)
                line_number = self._get_line_number(
                    option_name=option, line_dict=line_dict
                )
                option_node = OptionNode(
                    name=option,
                    location=line_number,
                    config_type=config_type,
                )
                parent.add_child(option_node)

                value = section[option]
                if value:
                    while value.startswith("\n"):
                        value = value[1:]

                    value = re.sub(r"\\\n\s*", "", value)
                    value = value.replace('"', "")

                    value_parts = value.split(",")
                    if len(value_parts) > 1:
                        value_parts = [x.strip() for x in value_parts]
                        value = str(value_parts)

                    value_node = ValueNode(name=value)
                    option_node.add_child(node=value_node)
                else:
                    logging.warning('Empty value in file "%s"', rel_file_path)
                    parent.children.remove(option_node)

        return artifact

    def _parse_gradle_build_file(
        self,
        abs_file_path: str,
        rel_file_path: str,
        root: Optional[ProjectNode],
    ) -> ArtifactNode:
        """Parse build.gradle and settings.gradle files using groovy-parser."""
        artifact = ArtifactNode(
            file_path=abs_file_path,
            rel_file_path=rel_file_path,
            concept_name=self.concept_name,
            project_root=root,
        )

        try:
            with open(abs_file_path, "r", encoding="utf-8") as file:
                content = file.read()

            # Parse the Groovy file
            tree = parse_groovy_content(content)

            # Extract configuration from the Lark Tree
            self._extract_config_from_tree(tree, artifact)

        except Exception as error:
            logging.warning(
                'Failed to parse Gradle file "%s" due to %s',
                rel_file_path,
                error
            )

        return artifact

    def _extract_config_from_tree(self, tree, parent_node):
        """Recursively extract configuration from Lark Tree."""
        from lark import Tree, Token

        if tree is None:
            return

        # Handle Tree nodes
        if isinstance(tree, Tree):
            rule_name = str(tree.data)

            # Handle command expressions (assignments and method calls)
            # These are processed as complete units, don't recurse after
            if rule_name == "command_expression":
                self._process_command_expression(tree, parent_node)
            else:
                # For non-command nodes, recursively process all children
                for child in tree.children:
                    self._extract_config_from_tree(child, parent_node)

    def _process_command_expression(self, tree, parent_node):
        """Process command expressions to extract assignments."""
        from lark import Tree, Token

        # Check if this is an assignment by recursively searching for ASSIGN token
        has_assignment = self._has_assign_token(tree)

        if has_assignment:
            # Extract the variable name and value
            var_name = None
            var_value = None

            # The structure is: command_expression -> expression -> expression (with assign)
            # First expression child contains the variable name and assign structure
            for child in tree.children:
                if isinstance(child, Tree) and str(child.data) == "expression":
                    # Look for identifier in the first nested expression
                    if var_name is None:
                        var_name = self._extract_identifier(child)

                    # Look for enhanced_statement_expression for the value
                    for subchild in child.children:
                        if isinstance(subchild, Tree) and str(subchild.data) == "enhanced_statement_expression":
                            var_value = self._extract_string_literal(subchild)

            if var_name and var_value:
                config_type = self.get_config_type(var_name, var_value)
                line_num = self._get_line_from_tree(tree)
                option_node = OptionNode(
                    name=var_name,
                    location=str(line_num),
                    config_type=config_type,
                )
                parent_node.add_child(option_node)
                value_node = ValueNode(name=var_value)
                option_node.add_child(value_node)
        else:
            # This might be a method call (like plugins { }, dependencies { })
            self._process_method_call(tree, parent_node)

    def _has_assign_token(self, tree):
        """Check if tree contains a top-level ASSIGN token (not inside closures)."""
        from lark import Tree, Token

        if isinstance(tree, Token) and tree.type == "ASSIGN":
            return True

        if isinstance(tree, Tree):
            # Don't recurse into closures - assignments inside closures
            # are not part of the current command_expression's assignment
            if str(tree.data) in ("closure", "closure_or_lambda_expression"):
                return False

            for child in tree.children:
                if self._has_assign_token(child):
                    return True

        return False

    def _process_method_call(self, tree, parent_node):
        """Process method calls like plugins { } and dependencies { }."""
        from lark import Tree

        # Extract method name
        method_name = None
        has_argument_list = False

        for child in tree.children:
            if isinstance(child, Tree):
                if str(child.data) == "argument_list":
                    has_argument_list = True
                elif method_name is None:
                    identifier = self._extract_identifier(child)
                    if identifier:
                        method_name = identifier

        if not method_name:
            return

        # Check if this is a simple method call with a string argument
        string_arg = self._extract_first_string_argument(tree)

        # Handle dependency declarations: use artifact coordinates as option name
        if string_arg and self._is_dependency_configuration(method_name):
            self._create_dependency_node(method_name, string_arg, tree, parent_node)
            return

        if string_arg:
            # This is a simple method call with an argument
            config_type = self.get_config_type(method_name, string_arg)
            line_num = self._get_line_from_tree(tree)
            option_node = OptionNode(
                name=method_name,
                location=str(line_num),
                config_type=config_type,
            )
            parent_node.add_child(option_node)
            value_node = ValueNode(name=string_arg)
            option_node.add_child(value_node)
        elif has_argument_list:
            # This is a method call with a closure/block (e.g., dependencies { ... })
            # Create a container node but don't recurse - let normal recursion handle children
            config_type = self.get_config_type(method_name)
            line_num = self._get_line_from_tree(tree)
            option_node = OptionNode(
                name=method_name,
                location=str(line_num),
                config_type=config_type,
            )
            parent_node.add_child(option_node)

            # Store this as a context so child nodes know their parent
            # The general recursion in _extract_config_from_tree will handle children
            # but we need to change the parent context for nodes inside this block
            # For now, do manual recursion with the correct parent
            for child in tree.children:
                if isinstance(child, Tree) and str(child.data) == "argument_list":
                    self._extract_config_from_tree(child, option_node)

    def _is_dependency_configuration(self, name):
        """Check if this is a dependency configuration."""
        return name in [
            "implementation",
            "api",
            "compileOnly",
            "runtimeOnly",
            "testImplementation",
            "testCompileOnly",
            "testRuntimeOnly",
            "androidTestImplementation",
            "debugImplementation",
            "releaseImplementation",
            "annotationProcessor",
            "kapt",
            "kaptTest",
        ]

    def _create_dependency_node(self, config_type, artifact, tree, parent_node):
        """Create a dependency node directly under the parent (which is the dependencies container).

        Only extracts dependencies with the pattern groupId:artifactId:version.
        Skips dependencies without versions or local project dependencies.

        Structure:
        dependencies (container - passed as parent_node)
          └─ groupId:artifactId (OptionNode)
              └─ version (ValueNode)

        Examples:
        - "org.springframework.boot:spring-boot-starter-web:2.7.0" → EXTRACTED
        - "junit:junit:4.13.2" → EXTRACTED
        - "org.apache.groovy:groovy-json" → SKIPPED (no version)
        - ":simple-jar" → SKIPPED (local project)
        """
        line_num = self._get_line_from_tree(tree)

        # Parse artifact coordinates to extract groupId:artifactId and version
        option_name, version = self._parse_artifact_coordinates(artifact)

        # Only add dependencies with the full groupId:artifactId:version pattern
        if not version:
            return  # Skip dependencies without version

        # Create option node for the dependency directly under parent (the dependencies container)
        option_node = OptionNode(
            name=option_name,
            location=str(line_num),
            config_type=ConfigType.NAME,
        )
        parent_node.add_child(option_node)

        # Add version as value
        value_node = ValueNode(name=version)
        option_node.add_child(value_node)

    def _parse_artifact_coordinates(self, artifact):
        """Parse artifact coordinates into groupId:artifactId and version.

        Only recognizes the pattern groupId:artifactId:version.
        Returns empty version for all other patterns (which will be skipped).

        Args:
            artifact: String like "group:artifact:version" or other patterns

        Returns:
            Tuple of (groupId:artifactId, version)
            - For "group:artifact:version": returns ("group:artifact", "version")
            - For all other patterns: returns (artifact, "")
        """
        parts = artifact.split(":")

        if len(parts) >= 3 and parts[0] and parts[1] and parts[2]:
            # Format: groupId:artifactId:version (all parts non-empty)
            # Join first two parts as option name, last part as version
            option_name = f"{parts[0]}:{parts[1]}"
            version = parts[2]
        else:
            # Any other format: return empty version to signal skipping
            option_name = artifact
            version = ""

        return option_name, version

    def _extract_first_string_argument(self, tree):
        """Extract the first string literal argument from a method call.

        Only extracts direct string arguments, not strings inside closures.
        For example:
        - `implementation 'artifact'` -> returns 'artifact'
        - `dependencies { implementation 'artifact' }` -> returns None
        """
        from lark import Tree

        # Look for argument_list -> ... -> string_literal (but not inside closures)
        for child in tree.children:
            if isinstance(child, Tree) and str(child.data) == "argument_list":
                # Check if this argument_list contains a closure
                # If it does, we should NOT extract strings from inside it
                if self._contains_closure(child):
                    return None
                # Otherwise, extract the first string literal
                result = self._extract_string_literal(child)
                if result:
                    return result
        return None

    def _contains_closure(self, tree):
        """Check if the tree contains a closure node."""
        from lark import Tree

        if isinstance(tree, Tree):
            if str(tree.data) in ("closure", "closure_or_lambda_expression"):
                return True
            for child in tree.children:
                if self._contains_closure(child):
                    return True
        return False

    def _extract_identifier(self, tree):
        """Extract identifier name from a tree."""
        from lark import Tree, Token

        if isinstance(tree, Token) and tree.type == "IDENTIFIER":
            # Token value is a tuple: (type, value, original)
            if isinstance(tree.value, tuple) and len(tree.value) >= 2:
                return str(tree.value[1])
            return str(tree.value)

        if isinstance(tree, Tree):
            for child in tree.children:
                result = self._extract_identifier(child)
                if result:
                    return result
        return None

    def _extract_string_literal(self, tree):
        """Extract string literal value from a tree."""
        from lark import Tree, Token

        if isinstance(tree, Token) and tree.type == "STRING_LITERAL":
            # Token value is a tuple: (type, value, original)
            if isinstance(tree.value, tuple) and len(tree.value) >= 2:
                value = str(tree.value[1])
            else:
                value = str(tree.value)

            # Value is already without quotes (extracted from the tuple)
            return value

        if isinstance(tree, Tree):
            for child in tree.children:
                result = self._extract_string_literal(child)
                if result:
                    return result
        return None

    def _get_line_from_tree(self, tree):
        """Get line number from a Lark tree."""
        from lark import Token

        # Try to find a token with line information
        if hasattr(tree, "meta") and tree.meta:
            return tree.meta.line if hasattr(tree.meta, "line") else "Unknown"

        # Recursively search for tokens with line info
        if hasattr(tree, "children"):
            for child in tree.children:
                if isinstance(child, Token):
                    if hasattr(child, "line"):
                        return child.line
                    # Token values are tuples: (type, value, original)
                    if isinstance(child.value, tuple) and len(child.value) >= 3:
                        return "Unknown"
        return "Unknown"

    def _get_line_number(self, option_name: str, line_dict: Dict) -> str:
        """Get line number from line dictionary."""
        for line in line_dict.keys():
            if option_name in line:
                lineno = line_dict[line]
                del line_dict[line]
                return str(lineno)
        return "Unknown"

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        if option_name.endswith((".home", ".projectcachedir")):
            return ConfigType.PATH

        if option_name.endswith(("max")):
            return ConfigType.NUMBER

        if option_name.endswith(".idletimeout"):
            return ConfigType.TIME

        if option_name.endswith(".worker.max"):
            return ConfigType.NUMBER

        if option_name.endswith(
            (
                ".caching",
                ".debug",
                ".configuration-cache",
                "configureondemand",
                ".daemon",
                ".isolated-projects",
                ".verbose",
                ".watch",
            )
        ):
            return ConfigType.BOOLEAN

        if option_name.endswith((".console", ".level", ".priority", ".mode")):
            return ConfigType.TYPE

        # Dependency artifacts (identified by special marker or colon separator)
        if option_name == "dependency" or ":" in option_name:
            return ConfigType.NAME

        # Additional patterns for build.gradle
        if option_name in ("version", "versionCode", "versionName") or "Version" in option_name:
            return ConfigType.VERSION_NUMBER

        if option_name in ("applicationId", "namespace", "group", "name"):
            return ConfigType.NAME

        if option_name in ("compileSdk", "minSdk", "targetSdk", "compileSdkVersion", "minSdkVersion", "targetSdkVersion"):
            return ConfigType.NUMBER

        if option_name in ("plugins", "repositories", "buildscript", "application", "ext", "dependencies"):
            return ConfigType.TYPE

        return super().get_config_type(option_name, value)
