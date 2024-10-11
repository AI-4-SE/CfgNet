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

    # pylint: disable=too-many-return-statements
    def get_config_type(self, option_name: str, value: str = "") -> ConfigType:
        if option_name in (
            "AccessFileName",
            "ErrorLog",
            "DocumentRoot",
            "Include",
            "IncludeOptional",
            "Options",
            "ServerRoot",
            "TransferLog",
            "DefaultIcon",
            "ReadmeName",
            "Files",
            "Alias",
            "AuthLDAPCharsetConfig",
            "DavGenericLockDB",
            "DavLockDB",
            "HeartbeatStorage",
            "MMapFile",
            "ScriptAlias",
            "ScriptLog",
            "ScriptSock",
            "TypesConfig",
            "DefaultIcon",
            "RewriteBase",
            "SessionInclude",
            "SessionExclude",
        ):
            return ConfigType.PATH

        if option_name in ("ErrorLogFormat", "AddType"):
            return ConfigType.TYPE

        if option_name in (
            "FlushMaxPipelined",
            "LimitInternalRecursion",
            "LimitRequestFields",
            "MaxKeepAliveRequests",
            "RLimitNPROC",
            "ServerLimit",
            "MaxSpareServers",
            "MinSpareServers",
            "StartServers",
            "HeartbeatMaxServers",
        ):
            return ConfigType.NUMBER

        if option_name in (
            "FlushMaxThreshold",
            "LimitRequestBody",
            "LimitRequestFieldSize",
            "LimitRequestLine",
            "LimitXMLRequestBody",
            "ReadBufferSize",
            "RLimitMEM",
        ):
            return ConfigType.SIZE

        if option_name in (
            "ServerAlias",
            "ServerName",
            "UnDefine",
            "HeaderName",
            "Group",
        ):
            return ConfigType.NAME

        if option_name in (
            "Location",
            "ServerPath",
            "AuthFormLoginRequiredLocation",
            "AuthFormLoginSuccessLocation",
            "AuthFormLogoutLocation",
            "AuthLDAPURL",
            "CacheKeyBaseURL",
            "MDCertificateAuthority",
            "MDHttpProxy",
            "RedirectPermanent",
            "RedirectTemp",
            "SSLOCSPProxyURL",
            "SSLStaplingForceURL",
        ):
            return ConfigType.URL

        if option_name in ("NameVirtualHost", "VirtualHost"):
            return ConfigType.IP_ADDRESS

        if option_name in (
            "KeepAliveTimeout",
            "RLimitCPU",
            "TimeOut",
            "CGIDScriptTimeout",
        ):
            return ConfigType.TIME

        if option_name in ("ServerAdmin"):
            return ConfigType.EMAIL

        if option_name in ("User"):
            return ConfigType.USERNAME

        return super().get_config_type(option_name, value)
