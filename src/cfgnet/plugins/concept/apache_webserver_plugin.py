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
from typing import Optional
import apacheconfig

from cfgnet.config_types.config_types import ConfigType
from cfgnet.plugins.plugin import Plugin
from cfgnet.network.nodes import (
    ArtifactNode,
    OptionNode,
    ProjectNode,
    ValueNode,
)


class ApacheWebserverPlugin(Plugin):
    def __init__(self):
        super().__init__("apache")

    def is_responsible(self, abs_file_path: str) -> bool:
        file_name = os.path.basename(abs_file_path)
        if file_name == "httpd.conf":
            return True
        return False

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

        with apacheconfig.make_loader() as loader:
            conf_dict = loader.load(abs_file_path)

        self.parse_conf_file(abs_file_path, conf_dict, artifact)
        return artifact

    def parse_conf_file(self, abs_file_path, conf_dict, artifact):
        multiple_options = {}
        nested_options = []

        for conf in conf_dict:
            if isinstance(conf_dict[conf], list):
                for value in conf_dict[conf]:
                    if isinstance(value, str):
                        multiple_options[conf] = conf_dict[conf]
                    else:
                        nested_options.append(
                            {
                                "conf": conf,
                                "block": list(value.keys())[0],
                                "options": list(value.values())[0],
                            }
                        )
            elif isinstance(conf_dict[conf], dict):
                nested_options.append(
                    {
                        "conf": conf,
                        "block": list(conf_dict[conf])[0],
                        "options": list(conf_dict[conf].values())[0],
                    }
                )

        unique_options = {}
        for conf in conf_dict:
            if type(conf_dict[conf]) not in (list, dict):
                unique_options[conf] = conf_dict[conf]

        self.parse_artifact(
            artifact,
            abs_file_path,
            unique_options,
            multiple_options,
            nested_options,
        )
        return artifact

    def parse_artifact(
        self,
        artifact,
        abs_file_path,
        unique_options,
        multiple_options,
        nested_options,
    ):
        with open(abs_file_path, "r", encoding="utf-8") as conffile:
            lines = conffile.readlines()
            self.parse_unique_options(artifact, lines, unique_options)
            self.parse_multiple_options(artifact, lines, multiple_options)
            self.parse_nested_options(artifact, lines, nested_options)

    def get_conf_value(self, values, parent, lineno):
        for value in values:
            if isinstance(values[value], dict):
                lineno += 1
                parent = self.parse_tree(parent, value, None, lineno)
                self.get_conf_value(list(values.values())[0], parent, lineno)
            else:
                lineno += 1
                self.parse_tree(parent, value, values[value], lineno)

    def parse_tree(self, artifact, option, value, lineno):
        config_type = self.get_config_type(option)
        option_node = OptionNode(
            name=option,
            location=lineno,
            config_type=config_type,
        )
        artifact.add_child(option_node)
        if value is not None:
            value_node = ValueNode(name=value)
            option_node.add_child(value_node)
        return option_node

    def parse_unique_options(self, artifact, lines, unique_options):
        start = 0
        for option in unique_options:
            for line in lines[start:]:
                if line[0] not in ("#", "\n"):
                    if line.startswith(option):
                        lineno = lines.index(line) + 1
                        value = unique_options[option]
                        self.parse_tree(artifact, option, value, lineno)
                        start = lineno
                        break

    def parse_multiple_options(self, artifact, lines, multiple_options):
        for option in multiple_options:
            start = 0
            for value in multiple_options[option]:
                for line in lines[start:]:
                    if line[0] not in ("#", "\n"):
                        if line.startswith(option):
                            lineno = lines.index(line) + 1
                            self.parse_tree(artifact, option, value, lineno)
                            start = lineno
                            break

    def parse_nested_options(self, artifact, lines, nested_options):
        block_type = False
        nested_conf = False
        lineno = 0

        for line in lines:
            if not block_type:
                if line[0] == "<":
                    for nested in nested_options:
                        if line.startswith("<" + nested["conf"]):
                            lineno = lines.index(line, lineno) + 1
                            parent = self.parse_tree(
                                artifact, nested["conf"], None, lineno
                            )
                            parent = self.parse_tree(
                                parent, nested["block"], None, lineno
                            )
                            block_type = True
                            break
            else:
                line_edit = line.replace(" ", "")
                if not nested_conf:
                    for option in nested["options"]:
                        if line_edit.startswith(
                            option
                        ) or line_edit.startswith("<" + option):
                            lineno = lines.index(line, lineno) + 1

                            if isinstance(nested_options[0]["options"], dict):
                                self.get_conf_value(
                                    nested_options[0]["options"],
                                    parent,
                                    lineno,
                                )
                                block_type = False
                                nested_options.remove(nested)
                                break

                            self.parse_tree(
                                parent,
                                option,
                                nested_options[0]["options"],
                                lineno,
                            )

                            if option == list(nested["options"])[-1]:
                                block_type = False
                                nested_options.remove(nested)
                            break

    def get_config_type(self, option_name: str) -> ConfigType:
        config_type = ConfigType.UNKNOWN
        if option_name in ("DefaultType", "TypesConfig", "LogLevel"):
            config_type = ConfigType.TYPE

        elif option_name in (
            "Directory",
            "DocumentRoot",
            "UserDir",
            "AccessFileName",
            "ErrorLog",
            "CustomLog",
            "DefaultIcon",
            "LoadModule",
            "AddIcon",
            "DirectoryIndex",
            "Files",
            "DAVLockDB",
            "ScriptAlias",
            "Location",
            "IndexOptions",
            "Options",
            "MIMEMagicFile",
        ):
            config_type = ConfigType.PATH

        elif option_name in ("Order", "Deny", "Allow"):
            config_type = ConfigType.LICENSE

        elif option_name in (
            "AddIconByType",
            "AddOutputFilter",
            "AddHandler",
            "AddDefaultCharset",
            "AddIconByEncoding",
            "IndexIgnore",
            "AddType",
            "IfModule",
            "SetHandler",
        ):
            config_type = ConfigType.COMMAND

        elif option_name == "User":
            config_type = ConfigType.USERNAME

        elif option_name == "ServerAdmin":
            config_type = ConfigType.EMAIL

        elif option_name in (
            "StartServers",
            "MinSpareServers",
            "MaxSpareServers",
            "ServerLimit",
            "MaxClients",
            "MaxRequestsPerChild",
            "ThreadsPerChild",
            "MinSpareThreads",
            "MaxSpareThreads",
            "Listen",
        ):
            config_type = ConfigType.NUMBER

        elif option_name in (
            "AllowOverride",
            "ExtendedStatus",
            "UseCanonicalName",
            "HostnameLookups",
            "ServerSignature",
        ):
            config_type = ConfigType.MODE

        elif option_name in (
            "ServerName",
            "ReadmeName",
            "HeaderName",
            "Group",
        ):
            config_type = ConfigType.NAME

        elif option_name in (
            "LanguagePriority",
            "ForceLanguagePriority",
            "AddLanguage",
            "LogFormat",
            "Alias",
        ):
            config_type = ConfigType.LANGUAGE

        elif option_name == "BrowserMatch":
            config_type = ConfigType.URL

        return config_type
