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


SEEN: Set[ast.Call] = set()


class MLPlugin(Plugin):
    modules_file: str

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
            modules = json.load(json_file)
        return modules

    # pylint: disable=W0703
    def _parse_config_file(
        self,
        abs_file_path: str,
        rel_file_path: str,
        root: Optional[ProjectNode],
    ) -> ArtifactNode:
        artifact = ArtifactNode(
            file_path=abs_file_path,
            rel_file_path=rel_file_path,
            concept_name=self.concept_name,
            project_root=root,
        )

        modules = MLPlugin.read_json(self.modules_file)

        try:
            with open(abs_file_path, "r", encoding="utf-8") as source:
                tree = ast.parse(source.read())

            SEEN.clear()

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    obj = node.value
                    target = node.targets[0]
                    if isinstance(obj, ast.Call):
                        SEEN.add(obj)
                        MLPlugin._parse_call(artifact, obj, target, modules)

                if isinstance(node, ast.Expr):
                    obj = node.value
                    if isinstance(obj, ast.Call):
                        if obj.args:
                            arg = obj.args[0]
                            SEEN.add(obj)
                            if isinstance(arg, ast.Call):
                                SEEN.add(arg)
                                MLPlugin._parse_call(
                                    artifact, arg, None, modules
                                )
                if isinstance(node, ast.Return):
                    if isinstance(node.value, ast.Call):
                        SEEN.add(node.value)
                        MLPlugin._parse_call(
                            artifact, node.value, None, modules
                        )

                if isinstance(node, ast.Call):
                    if node not in SEEN:
                        MLPlugin._parse_call(artifact, node, None, modules)

        except Exception as error:
            logging.error(
                "Failed to parse %s due to %s: %s",
                abs_file_path,
                type(error).__name__,
                error,
            )

        return artifact

    @staticmethod
    def _parse_call(
        parent: ArtifactNode, obj: ast.Call, target: Any, data: Dict
    ):
        func = obj.func
        keywords = obj.keywords
        args = obj.args
        if isinstance(func, ast.Name):
            if any(func.id == module["name"] for module in data):
                module = MLPlugin._find_module(func.id, data)
                option = OptionNode(name=func.id, location=str(func.lineno))
                parent.add_child(option)

                # Variable
                if target:
                    if isinstance(target, ast.Name):
                        MLPlugin._parse_variable(target, option)

                # Arguments
                if args:
                    MLPlugin._parse_args(args, option, module)

                # Keywords
                if keywords:
                    MLPlugin._parse_keywords(keywords, option)

                if not option.children:
                    parent.children.remove(option)

        if isinstance(func, ast.Attribute):
            if isinstance(func.value, ast.Call):
                SEEN.add(func.value)
                MLPlugin._parse_call(parent, func.value, target, data)
            if any(func.attr == module["name"] for module in data):
                module = MLPlugin._find_module(func.attr, data)
                option = OptionNode(name=func.attr, location=str(func.lineno))
                parent.add_child(option)

                # Variable
                if target:
                    if isinstance(target, ast.Name):
                        MLPlugin._parse_variable(target, option)

                # Arguments
                if args:
                    MLPlugin._parse_args(args, option, module)

                # Keywords
                if keywords:
                    MLPlugin._parse_keywords(keywords, option)

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

    @staticmethod
    def _parse_keywords(keywords: List, parent: OptionNode) -> None:
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
                        arg_value = ValueNode(name=key.value.id)
                        argument.add_child(arg_value)
                    else:
                        value_name = ast.unparse(key.value)
                        if value_name.startswith("'") and value_name.endswith(
                            "'"
                        ):
                            value_name = value_name.replace("'", "")
                        value = ValueNode(name=value_name)
                        argument.add_child(value)

    @staticmethod
    def _parse_args(args: List, parent: OptionNode, module: Dict) -> None:
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
                    arg_value = ValueNode(name=arg.id)
                    arg_option.add_child(arg_value)
                else:
                    value_name = ast.unparse(arg)
                    if value_name.startswith("'") and value_name.endswith("'"):
                        value_name = value_name.replace("'", "")
                    value = ValueNode(name=value_name)
                    arg_option.add_child(value)

    @staticmethod
    def _find_module(name: str, data: Dict) -> Dict:
        """Find the correct sci kit learn module based on a given name."""
        module = next(filter(lambda x: name == x["name"], data))
        return module
