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
from typing import Optional, Dict, List, Set, Tuple

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
            """Parse build.gradle and settings.gradle files.

            We use groovy-parser as the primary extraction mechanism, but Gradle/Groovy
            DSL has many constructs that are hard to recover losslessly from the AST
            (e.g., method-call RHS assignments, nested blocks, plugin DSL, dependency
            notations, etc.). To ensure we extract *all* potential options, we run an
            additional lightweight, line-based extractor that:
              - extracts every "=" assignment (including dotted keys like xml.enabled)
              - parses the plugins { } DSL (id -> version)
              - parses the dependencies { } DSL (group:artifact -> version, and other notations as raw values)
            """
            artifact = ArtifactNode(
                file_path=abs_file_path,
                rel_file_path=rel_file_path,
                concept_name=self.concept_name,
                project_root=root,
            )

            try:
                with open(abs_file_path, "r", encoding="utf-8") as file:
                    content = file.read()

                # Used to de-duplicate nodes across AST + regex passes
                self._seen_option_value_locations = set()

                # 1) AST-based extraction (best-effort)
                try:
                    tree = parse_groovy_content(content)
                    self._extract_config_from_tree(tree, artifact)
                except Exception as error:  # keep parsing via regex below
                    logging.warning(
                        'Failed to parse Gradle file "%s" with groovy-parser due to %s',
                        rel_file_path,
                        error,
                    )

                # 2) Regex/line-based extraction (completeness-oriented)
                self._extract_config_from_text(content, artifact)

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
                line_num = self._get_line_from_tree(tree)
                self._add_option_value(parent_node, var_name, var_value, line_num)
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
            line_num = self._get_line_from_tree(tree)
            self._add_option_value(parent_node, method_name, string_arg, line_num)
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

        
    def _get_or_create_option_node(self, parent_node, option_name: str, line_num: str = "Unknown"):
        """Return an existing OptionNode child with the given name, or create it once."""
        if option_name is None or option_name == "":
            return None

        cache = getattr(self, "_option_node_cache", None)
        if not isinstance(cache, dict):
            cache = {}
            setattr(self, "_option_node_cache", cache)

        key = (id(parent_node), option_name)
        if key in cache:
            return cache[key]

        config_type = self.get_config_type(option_name, "")
        option_node = OptionNode(
            name=option_name,
            location=str(line_num) if line_num is not None else "Unknown",
            config_type=config_type,
        )
        parent_node.add_child(option_node)
        cache[key] = option_node
        return option_node


    def _add_option_value(
        self,
        parent_node,
        option_name: str,
        value: str,
        line_num: str = "Unknown",
    ) -> None:
        """Add an option/value node pair with best-effort de-duplication (per parent + option + value)."""
        if option_name is None or option_name == "":
            return

        value_str = "" if value is None else str(value).strip()
        loc_str = str(line_num) if line_num is not None else "Unknown"

        seen = getattr(self, "_seen_option_values", None)
        if not isinstance(seen, set):
            seen = set()
            setattr(self, "_seen_option_values", seen)

        key = (id(parent_node), option_name, value_str)
        if key in seen:
            return
        seen.add(key)

        option_node = self._get_or_create_option_node(parent_node, option_name, loc_str)
        if option_node is None:
            return

        if value_str != "":
            value_node = ValueNode(name=value_str)
            option_node.add_child(value_node)

    def _strip_inline_comment(self, line: str) -> str:
        """Remove // comments from a line, keeping content inside quotes."""
        out = []
        in_single = False
        in_double = False
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == "'" and not in_double:
                in_single = not in_single
                out.append(ch)
                i += 1
                continue
            if ch == '"' and not in_single:
                in_double = not in_double
                out.append(ch)
                i += 1
                continue
            # start of // comment outside quotes
            if not in_single and not in_double and ch == "/" and i + 1 < len(line) and line[i + 1] == "/":
                break
            out.append(ch)
            i += 1
        return "".join(out)

    
    def _extract_config_from_text(self, content: str, parent_node) -> None:
        """Completeness-oriented extraction over raw text with hierarchical block paths.

        - Creates OptionNodes for named blocks like: jmh { ... }  /  reports { ... }
        - Extracts any "=" assignment under the current block path (supports dotted keys)
        - Extracts plugins DSL: id -> version under plugins { ... }
        - Extracts dependencies DSL under dependencies { ... }:
            * "g:a:v" -> option "g:a", value "v"
            * "g:a" (no version) -> option "<configuration>", value "g:a"
        - Skips dynamic/imperative closures such as: [..].each { ... } and tasks.register(...) { ... }
        """
        in_block_comment = False

        # Node stack mirrors created named blocks; starts at artifact node
        node_stack = [parent_node]
        name_stack: List[str] = []

        # Brace stack tracks *all* opens so closes pop correctly.
        # Each entry is ("NODE", block_name) or ("SKIP", None) or ("NONE", None)
        brace_stack: List[Tuple[str, Optional[str]]] = []

        # Regexes
        re_named_block_open = re.compile(r"^\s*([A-Za-z_][\w\-]*)\s*\{\s*$")
        re_assignment = re.compile(r"^\s*([A-Za-z_][\w\.\-]*)\s*=\s*(.+?)\s*$")
        re_plugins_id = re.compile(
            r"\bid\s*(?:\(\s*)?['\"]([^'\"]+)['\"]\s*(?:\)\s*)?"
            r"(?:\s*version\s*['\"]([^'\"]+)['\"])?",
        )
        re_apply_plugin = re.compile(r"\bapply\s+plugin\s*:\s*['\"]([^'\"]+)['\"]")
        re_dep_decl = re.compile(r"^\s*([A-Za-z_][\w]*)\s*(?:\(|\s+)\s*(.+?)\s*\)?\s*$")
        re_quoted = re.compile(r"^['\"]([^'\"]*)['\"]$")

        def skip_active() -> bool:
            return any(k == "SKIP" for k, _ in brace_stack)

        def current_ctx() -> str:
            return name_stack[-1] if name_stack else ""

        def push_named_block(block_name: str, lineno: int):
            # Create/reuse block node as OptionNode
            if skip_active():
                brace_stack.append(("NONE", None))
                return
            parent = node_stack[-1]
            block_node = self._get_or_create_option_node(parent, block_name, str(lineno))
            node_stack.append(block_node)
            name_stack.append(block_name)
            brace_stack.append(("NODE", block_name))

        def push_skip_block():
            brace_stack.append(("SKIP", None))

        def push_none():
            brace_stack.append(("NONE", None))

        def pop_one():
            if not brace_stack:
                return
            kind, block_name = brace_stack.pop()
            if kind == "NODE":
                # Pop the corresponding named block from stacks
                if node_stack:
                    node_stack.pop()
                if name_stack:
                    name_stack.pop()

        lines = content.splitlines()
        for lineno, raw in enumerate(lines, start=1):
            line = raw.rstrip("\n")

            # Handle /* ... */ comments (best-effort, line-based)
            if in_block_comment:
                if "*/" in line:
                    in_block_comment = False
                    line = line.split("*/", 1)[1]
                else:
                    # Still need to account for braces? assume none in block comments.
                    continue

            if "/*" in line:
                before, after = line.split("/*", 1)
                if "*/" in after:
                    after = after.split("*/", 1)[1]
                    line = before + after
                else:
                    in_block_comment = True
                    line = before

            line = self._strip_inline_comment(line).strip()
            if not line:
                continue

            # Pre-count braces (approx; braces in strings are rare in Gradle scripts)
            open_count = line.count("{")
            close_count = line.count("}")

            # Detect and push openings in a way that preserves hierarchy
            # 1) Skip dynamic closures: [..].each { ... }  or  tasks.register(..) { ... }
            if open_count > 0 and (
                (".each" in line and "{" in line)
                or ("tasks.register" in line and "{" in line)
                or ("tasks.withType" in line and "{" in line)
                or (re.match(r"^\s*dependencyRecommendations\s*\{\s*$", line) is not None)
            ):
                # Push one SKIP for the first "{"; any additional "{" are NONE
                push_skip_block()
                for _ in range(max(0, open_count - 1)):
                    push_none()
            else:
                # 2) Named block open (exact form: name { )
                m_open = re_named_block_open.match(line)
                if m_open and open_count == 1 and close_count == 0:
                    push_named_block(m_open.group(1), lineno)
                else:
                    # 3) Generic opens we don't model as config sections
                    for _ in range(open_count):
                        push_none()

            # If we're in a skipped region, ignore extraction but still pop closes
            if not skip_active():
                ctx = current_ctx()

                # --- plugins { } DSL
                if ctx == "plugins":
                    m = re_plugins_id.search(line)
                    if m:
                        plugin_id = m.group(1)
                        plugin_version = (m.group(2) or "").strip()
                        # Desired shape:
                        #   <file>::::plugins::::<plugin_id>::::version::::<plugin_version>
                        if plugin_version != "":
                            plugin_node = self._get_or_create_option_node(node_stack[-1], plugin_id, str(lineno))
                            if plugin_node is not None:
                                self._add_option_value(plugin_node, "version", plugin_version, str(lineno))

                # --- apply plugin: '...'
                m_apply = re_apply_plugin.search(line)
                if m_apply:
                    plugin_id = m_apply.group(1)
                    self._add_option_value(node_stack[-1], plugin_id, "", str(lineno))

                # --- dependencies { } DSL
                if ctx == "dependencies":
                    m = re_dep_decl.match(line)
                    if m:
                        conf = m.group(1)
                        spec = m.group(2).strip()

                        # Prefer a quoted coordinate inside the spec
                        quoted = re.findall(r"['\"]([^'\"]+)['\"]", spec)
                        candidate = quoted[0] if quoted else spec

                        option_name, version = self._parse_artifact_coordinates(candidate)
                        if version:
                            # g:a:v  -> option g:a, value v  (no conf in key)
                            self._add_option_value(node_stack[-1], option_name, version, str(lineno))
                        else:
                            # g:a (no version) -> option conf, value candidate
                            self._add_option_value(node_stack[-1], conf, candidate, str(lineno))

                # --- generic "=" assignments (everywhere, under current block path)
                m_assign = re_assignment.match(line)
                if m_assign:
                    key = m_assign.group(1).strip()
                    rhs = m_assign.group(2).strip().rstrip(",")

                    mq = re_quoted.match(rhs)
                    if mq:
                        rhs = mq.group(1)

                    self._add_option_value(node_stack[-1], key, rhs, str(lineno))

            # Pop closes at end of line
            for _ in range(close_count):
                pop_one()


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
