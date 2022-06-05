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

import re
import ast
import json
import logging
from typing import Dict, Optional, Set, Any, List
from cfgnet.plugins.plugin import Plugin
from cfgnet.network.nodes import (
    Node,
    ProjectNode,
    ArtifactNode,
    OptionNode,
    ValueNode,
)
from cfgnet.utility.cfg import Cfg


SEEN: Set[Any] = set()
MODULE_REGEX = re.compile(r"(?P<call>(\w+\._*)*(\w+){1})(?P<params>\(.*\))")


class MLPlugin(Plugin):
    modules_file: str
    cfg: Cfg
    module_data: Dict
    imports: List

    def __init__(self, name: str):
        super().__init__(name)

    @staticmethod
    def read_json(file_path: str) -> Dict:
        """
        Read modules from json file.

        :param: path to file that contains the modules
        :return: dict of modules
        """
        with open(file_path, "r", encoding="utf-8") as json_file:
            module_data = json.load(json_file)
        return module_data

    # pylint: disable=W0703
    def _parse_config_file(
        self,
        abs_file_path: str,
        rel_file_path: str,
        root: Optional[ProjectNode],
    ) -> ArtifactNode:

        SEEN.clear()

        artifact = ArtifactNode(
            file_path=abs_file_path,
            rel_file_path=rel_file_path,
            concept_name=self.concept_name,
            project_root=root,
        )

        self.module_data = MLPlugin.read_json(self.modules_file)

        try:
            with open(abs_file_path, "r", encoding="utf-8") as source:
                code_str = source.read()
                tree = ast.parse(code_str)
                self.get_imports(tree)
                self.cfg = Cfg(code_str=code_str)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node not in SEEN:
                    self.parse_class_def(node=node, parent=artifact)

                if isinstance(node, ast.Assign) and node not in SEEN:
                    self.parse_assign(node=node, parent=artifact)

                if isinstance(node, ast.Call) and node not in SEEN:
                    if self.is_module(node):
                        self.parse_call(
                            node=node, parent=artifact, target=None
                        )

        except Exception as error:
            logging.error(
                "Failed to parse %s due to %s: %s",
                abs_file_path,
                type(error).__name__,
                error,
            )

        return artifact

    def parse_class_def(self, node: ast.ClassDef, parent: Node) -> None:
        class_option = OptionNode(name=node.name, location=str(node.lineno))
        parent.add_child(class_option)

        is_ml_class = False

        base_counter = 0
        for base in node.bases:
            if self.is_module(base):
                base_name = ast.unparse(base).rsplit(".", maxsplit=1)[-1]
                module = self.find_module(base_name)
                if module:
                    base_class = OptionNode(
                        name=f"base_class_{base_counter}",
                        location=str(node.lineno),
                    )
                    class_option.add_child(base_class)
                    base_class.add_child(ValueNode(name=module["full_name"]))
                    base_counter += 1
                    is_ml_class = True

        if class_option.children:
            if is_ml_class:
                self.parse_class_body(body=node.body, parent=class_option)
        else:
            parent.children.remove(class_option)

    def parse_class_body(self, body: List, parent: Node) -> None:
        for node in body:
            if isinstance(node, ast.FunctionDef):
                if node.name == "__init__":
                    self.parse_func_body(node.body, parent)

    def parse_func_body(self, body: List, parent: Node) -> None:
        for node in body:
            if isinstance(node, ast.Assign):
                SEEN.add(node)
                self.parse_assign(node, parent)

    def parse_assign(self, node: ast.Assign, parent: Node) -> None:
        obj = node.value
        target = node.targets[0]
        if isinstance(obj, ast.Call):
            SEEN.add(obj)
            if self.is_module(obj):
                self.parse_call(node=obj, parent=parent, target=target)

    # flake8: noqa: C901
    def parse_call(self, node: ast.Call, parent: Node, target: Any):
        """
        Parse ast.Call object and extract corresponding nodes.

        :param node: ast.Call node object
        :param parent: parent node
        """
        SEEN.add(node)
        func = node.func
        keywords = node.keywords
        args = node.args
        if isinstance(func, ast.Name):
            if any(func.id == module["name"] for module in self.module_data):
                module = self.find_module(func.id)
                if module:
                    option = OptionNode(
                        name=func.id, location=str(func.lineno)
                    )
                    parent.add_child(option)

                    # Variable
                    if target:
                        self.parse_target(target, option)

                    # Arguments
                    if args:
                        self.parse_arguments(args, option, module)

                    # Keywords
                    if keywords:
                        self.parse_keywords(keywords, option)

                    if not args and not keywords:
                        params = OptionNode(
                            name="params", location=str(func.lineno)
                        )
                        option.add_child(params)
                        value_node = ValueNode(name="default")
                        params.add_child(value_node)

                    if not option.children:
                        parent.children.remove(option)

        if isinstance(func, ast.Attribute):
            if isinstance(func.value, ast.Call):
                SEEN.add(func.value)
                if self.is_module(func.value):
                    self.parse_call(
                        node=func.value, parent=parent, target=target
                    )
            if any(func.attr == module["name"] for module in self.module_data):
                module = self.find_module(func.attr)
                if module:
                    option = OptionNode(
                        name=func.attr, location=str(func.lineno)
                    )
                    parent.add_child(option)

                    # Variable
                    if target:
                        self.parse_target(target, option)

                    # Arguments
                    if args:
                        self.parse_arguments(args, option, module)

                    # Keywords
                    if keywords:
                        self.parse_keywords(keywords, option)

                    if not args and not keywords:
                        params = OptionNode(
                            name="params", location=str(func.lineno)
                        )
                        option.add_child(params)
                        value_node = ValueNode(name="default")
                        params.add_child(value_node)

    def parse_keywords(self, keywords: List, parent: OptionNode) -> None:
        """
        Extract all parameters and their values and create corresponding nodes.

        :param keywords: list of parameters
        :param parent: parent option node
        """
        for key in keywords:
            if isinstance(key, ast.keyword):
                if key.arg:
                    argument = OptionNode(
                        name=key.arg, location=str(parent.location)
                    )
                    parent.add_child(argument)
                    if isinstance(key.value, ast.Name):
                        possible_values = self.cfg.compute_values(
                            var=key.value.id
                        )
                        arg_value = ValueNode(
                            name=key.value.id, possible_values=possible_values
                        )
                        argument.add_child(arg_value)
                    else:
                        value_name = ast.unparse(key.value)
                        if value_name.startswith("'") and value_name.endswith(
                            "'"
                        ):
                            value_name = value_name.replace("'", "")
                        value = ValueNode(name=value_name)
                        argument.add_child(value)

    def parse_arguments(self, args: List, parent: Node, module: Dict) -> None:
        """
        Extract all arguments and create corresponding nodes.

        :param args: list of arguments
        :param parent: parent option node
        """
        params = module["params"]
        if params:
            for i, arg in enumerate(args):
                option_name = params[i]
                arg_option = OptionNode(
                    name=option_name, location=str(arg.lineno)
                )
                parent.add_child(arg_option)
                if isinstance(arg, ast.Name):
                    possible_values = self.cfg.compute_values(var=arg.id)
                    arg_value = ValueNode(
                        name=arg.id, possible_values=possible_values
                    )
                    arg_option.add_child(arg_value)
                else:
                    value_name = ast.unparse(arg)
                    if value_name.startswith("'") and value_name.endswith("'"):
                        value_name = value_name.replace("'", "")
                    value = ValueNode(name=value_name)
                    arg_option.add_child(value)

    @staticmethod
    def parse_target(var: Any, parent: Node) -> None:
        """
        Extract variable name and create corresponding nodes.

        :param var: variable
        :param parent: parent option node
        """
        option_var = OptionNode(name="variable", location=str(var.lineno))
        parent.add_child(option_var)
        name = ast.unparse(var).replace("'", "")
        var_node = ValueNode(name=name)
        option_var.add_child(var_node)

    def is_module(self, node: Any) -> bool:
        """
        Check if the given node belongs to the imported ML algorithms.

        The call of an ML algorithm needs to match an import statement.
        ML modules can either be directly imported or invoked using an alias.
        For instance, we check the first element as an alias might be used
        to call the ML algorithm.

        :param node: node to check
        :return: True if node belongs to imported ML algorithm else False
        """
        match = MODULE_REGEX.fullmatch(ast.unparse(node))
        if match:
            node_str = match.group("call")
            node_parts = node_str.split(".")
        else:
            node_parts = ast.unparse(node).split(".")

        if any(name == node_parts[0] for name in self.imports):
            return True

        if any(name == node_parts[-1] for name in self.imports):
            return False

        return False

    def find_module(self, name: str) -> Optional[Dict]:
        """
        Find the correct sci kit learn module based on a given name the extracted imports.

        :param name: Name if module to be found
        :param data: data dictionary of ML modules
        :param imports: list of ML import
        :return: dictionary of the ML module
        """
        try:
            module = next(
                filter(lambda x: name == x["name"], self.module_data)
            )
            return module
        except StopIteration:
            return None

    # pylint: disable=cell-var-from-loop
    def get_imports(self, tree: ast.Module) -> None:
        """
        Find all used ML modules and return dict with their data.

        :param tree: ast tree
        :param modules_data: dictionary of the ML module data
        :return: list of imports
        """
        self.imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for package in node.names:
                    if self.concept_name == package.name:
                        if package.asname:
                            self.imports.append(package.asname)
                        else:
                            self.imports.append(package.name)

            if isinstance(node, ast.ImportFrom):
                for package in node.names:
                    if node.module:
                        module = node.module.split(".")[0]
                        if self.concept_name == module:
                            if package.asname:
                                self.imports.append(package.asname)
                            else:
                                self.imports.append(package.name)
