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

import ast
import json
import logging
from typing import Dict, Optional, Set, Any, List
from cfgnet.plugins.plugin import Plugin
from cfgnet.network.nodes import (
    ProjectNode,
    ArtifactNode,
    OptionNode,
    ValueNode,
)
from cfgnet.utility.cfg import Cfg


SEEN: Set[ast.Call] = set()


class MLPlugin(Plugin):
    modules_file: str
    cfg: Cfg

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

        module_data = MLPlugin.read_json(self.modules_file)

        try:
            with open(abs_file_path, "r", encoding="utf-8") as source:
                code_str = source.read()
                tree = ast.parse(code_str)
                imports = MLPlugin.get_imports(tree)

                self.cfg = Cfg(code_str=code_str)

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    obj = node.value
                    target = node.targets[0]
                    if isinstance(obj, ast.Call):
                        SEEN.add(obj)
                        self._parse_call(
                            artifact, obj, target, module_data, imports
                        )

                if isinstance(node, ast.Expr):
                    obj = node.value
                    if isinstance(obj, ast.Call):
                        if obj.args:
                            arg = obj.args[0]
                            SEEN.add(obj)
                            if isinstance(arg, ast.Call):
                                SEEN.add(arg)
                                self._parse_call(
                                    artifact, arg, None, module_data, imports
                                )
                if isinstance(node, ast.Return):
                    if isinstance(node.value, ast.Call):
                        SEEN.add(node.value)
                        self._parse_call(
                            artifact, node.value, None, module_data, imports
                        )

                if isinstance(node, ast.Call):
                    if node not in SEEN:
                        self._parse_call(
                            artifact, node, None, module_data, imports
                        )

        except Exception as error:
            logging.error(
                "Failed to parse %s due to %s: %s",
                abs_file_path,
                type(error).__name__,
                error,
            )

        return artifact

    # flake8: noqa: C901
    def _parse_call(
        self,
        parent: ArtifactNode,
        obj: ast.Call,
        target: Any,
        data: Dict,
        imports: List,
    ):
        """
        Parse ast.Call object and extract corresponding nodes.

        :param parent: artifact node of the file to be parsed
        :param obj: ast.Call object
        :param target: variable name if obj come from ast.Assign else None
        :param data: data dictionary of ML modules
        """
        func = obj.func
        keywords = obj.keywords
        args = obj.args
        if isinstance(func, ast.Name):
            if any(func.id == module["name"] for module in data):
                module = MLPlugin._find_module(func.id, data, imports)
                if module:
                    option = OptionNode(
                        name=func.id, location=str(func.lineno)
                    )
                    parent.add_child(option)

                    # Variable
                    if target:
                        if isinstance(target, ast.Name):
                            MLPlugin._parse_variable(target, option)

                    # Arguments
                    if args:
                        self._parse_args(args, option, module)

                    # Keywords
                    if keywords:
                        self._parse_keywords(keywords, option)

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
                self._parse_call(parent, func.value, target, data, imports)
            if any(func.attr == module["name"] for module in data):
                module = MLPlugin._find_module(func.attr, data, imports)
                if module:
                    option = OptionNode(
                        name=func.attr, location=str(func.lineno)
                    )
                    parent.add_child(option)

                    # Variable
                    if target:
                        if isinstance(target, ast.Name):
                            MLPlugin._parse_variable(target, option)

                    # Arguments
                    if args:
                        self._parse_args(args, option, module)

                    # Keywords
                    if keywords:
                        self._parse_keywords(keywords, option)

                    if not args and not keywords:
                        params = OptionNode(
                            name="params", location=str(func.lineno)
                        )
                        option.add_child(params)
                        value_node = ValueNode(name="default")
                        params.add_child(value_node)

    @staticmethod
    def _parse_variable(var: ast.Name, parent: OptionNode) -> None:
        """
        Extract variable name and create corresponding nodes.

        :param var: variable
        :param parent: parent option node
        """
        option_var = OptionNode(name="variable", location=str(var.lineno))
        parent.add_child(option_var)
        var_name = ValueNode(name=var.id)
        option_var.add_child(var_name)

    def _parse_keywords(self, keywords: List, parent: OptionNode) -> None:
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
                    if isinstance(key.value, ast.Constant):
                        arg_value = ValueNode(name=key.value.value)
                        argument.add_child(arg_value)
                    elif isinstance(key.value, ast.Name):
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

    def _parse_args(
        self, args: List, parent: OptionNode, module: Dict
    ) -> None:
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
                if isinstance(arg, ast.Compare):
                    if isinstance(arg.comparators[0], ast.Name):
                        arg_value = ValueNode(name=arg.comparators[0].id)
                        arg_option.add_child(arg_value)
                elif isinstance(args[i], ast.Constant):
                    arg_value = ValueNode(name=arg.value)
                    arg_option.add_child(arg_value)
                elif isinstance(arg, ast.Name):
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
    def _find_module(name: str, data: Dict, imports) -> Optional[Dict]:
        """
        Find the correct sci kit learn module based on a given name the extracted imports.

        :param name: Name if module to be found
        :param data: data dictionary of ML modules
        :param imports: list of ML import
        :return: dictionary of the ML module
        """
        module = next(filter(lambda x: name == x["name"], data))

        full_name = module["full_name"]

        if any(name in full_name for name in imports):
            return module

        return None

    # pylint: disable=cell-var-from-loop
    @staticmethod
    def get_imports(tree: ast.Module) -> List:
        """
        Find all used ML modules and return dict with their data.

        :param tree: ast tree
        :param modules_data: dictionary of the ML module data
        :return: list of imports
        """
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                name = node.module
                alias_list = node.names
                for alias in alias_list:
                    if isinstance(alias, ast.alias):
                        full_name = f"{name}.{alias.name}"
                        imports.append(full_name)
            if isinstance(node, ast.Import):
                alias_list = node.names
                for alias in alias_list:
                    if isinstance(alias, ast.alias):
                        imports.append(alias.name)

        return imports
