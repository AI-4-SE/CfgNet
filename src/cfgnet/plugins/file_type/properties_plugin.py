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

import logging
import os

from jproperties import Properties, PropertyError

from cfgnet.network.nodes import ArtifactNode, OptionNode, ValueNode
from cfgnet.plugins.plugin import Plugin


class PropertiesPlugin(Plugin):
    """
    Plugin for parsing Java :code:`.properties` files.

    We use the PyPi properties parser jproperties. For more details see:
    https://pypi.org/project/jproperties/

    Additionally to the rules implemented by the jproperties parser
    we allow sections in the properties files:
    lines, that start with :code:`[` and end with :code:`]` are handled like
    section in INI files.  Note that in this case the first occurrence of
    :code:`=` or :code:`:` will be ignored (i.e. :code:`[a=b:c]` is equivalent
    to :code:`[a:b:c]` and :code:`[a b:c]`).

    Also keep in mind, that options have to be unique otherwise only the last
    appearance of an option will be processed, i.e. if a properties file has the
    following content:

    .. code::

        option=value1
        option=value2

    The parser will create only one value node with
    :code:`id ...option::::value2`.
    """

    def __init__(self):
        super().__init__("properties")

    def _parse_config_file(self, abs_file_path, rel_file_path, concept_root):
        """
        Create an artifact node from information given in a properties file.

        :param abs_file_path: absolute file path to the properties file
        :param rel_file_path: relative file path to the properties file
        :param concept_root: concept node that gets this artifact node as child
        :param content: content of a properties file (alternative to the
            property file)
        :return: artifact node
        """
        file_name = os.path.basename(abs_file_path)
        artifact = ArtifactNode(
            file_name, abs_file_path, rel_file_path, concept_root
        )

        properties = Properties()

        # try to parse properties_file using jproperties
        try:
            with open(abs_file_path, "rb") as properties_file:
                properties.load(properties_file, "utf-8")
                section_node = artifact
                for option in properties:
                    value, _ = properties[option]

                    # identify section headers and handle them
                    if option.startswith("["):
                        if value.strip().endswith("]"):
                            section_name = (option + " " + value.strip())[1:-1]
                        elif option.endswith("]") and not value:
                            section_name = option.strip()[1:-1]
                        else:
                            section_name = option[1:]
                        section_node = OptionNode(
                            section_name, "section: " + section_name
                        )
                        artifact.add_child(section_node)

                    # if a line doesn't contain a section header it contains an
                    # option
                    else:
                        option_node = OptionNode(option, "option: " + option)
                        section_node.add_child(option_node)
                        value_node = ValueNode(value)
                        option_node.add_child(value_node)

        except PropertyError as error:
            logging.warning(
                'Failed to parse properties file "%s" with jproperties due to %s',
                rel_file_path,
                error,
            )

        return artifact

    def is_responsible(self, abs_file_path):
        if abs_file_path.endswith(".properties"):
            return True

        return False
