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

from typing import List, Optional

from cfgnet.plugins.plugin import Plugin
from cfgnet.plugins.concept.docker_plugin import DockerPlugin
from cfgnet.plugins.concept.maven_plugin import MavenPlugin
from cfgnet.plugins.concept.nodejs_plugin import NodejsPlugin
from cfgnet.plugins.concept.cypress_plugin import CypressPlugin
from cfgnet.plugins.concept.tsconfig_plugin import TsconfigPlugin
from cfgnet.plugins.concept.travis_plugin import TravisPlugin
from cfgnet.plugins.concept.docker_compose_plugin import DockerComposePlugin
from cfgnet.plugins.concept.poetry_plugin import PoetryPlugin
from cfgnet.plugins.concept.spring_plugin import SpringPlugin
from cfgnet.plugins.concept.apache_webserver_plugin import (
    ApacheWebserverPlugin,
)
from cfgnet.plugins.file_type.configparser_plugin import ConfigParserPlugin
from cfgnet.plugins.file_type.yaml_plugin import YAMLPlugin
from cfgnet.plugins.file_type.toml_plugin import TomlPlugin
from cfgnet.plugins.file_type.hadoop_plugin import HadoopPlugin
from cfgnet.plugins.concept.mysql_plugin import MysqlPlugin
from cfgnet.plugins.concept.ansible_plugin import AnsiblePlugin
from cfgnet.plugins.concept.ansible_playbook_plugin import (
    AnsiblePlaybookPlugin,
)
from cfgnet.plugins.concept.postgresql_plugin import PostgreSQLPlugin
from cfgnet.plugins.concept.mongodb_plugin import MongoDBPlugin
from cfgnet.plugins.concept.django_plugin import DjangoPlugin
from cfgnet.plugins.concept.zookeeper_plugin import ZookeeperPlugin
from cfgnet.plugins.concept.alluxio_plugin import AlluxioPlugin

from cfgnet.plugins.concept.hadoop_common_plugin import HadoopCommonPlugin
from cfgnet.plugins.concept.hadoop_hdfs_plugin import HadoopHdfsPlugin
from cfgnet.plugins.concept.hadoop_hbase_plugin import HadoopHbasePlugin
from cfgnet.plugins.concept.yarn_plugin import YarnPlugin
from cfgnet.plugins.concept.elastisearch_plugin import ElasticsearchPlugin
from cfgnet.plugins.concept.kafka_plugin import KafkaPlugin
from cfgnet.plugins.concept.angular_plugin import AngularPlugin
from cfgnet.plugins.concept.mapreduce_plugin import MapReducePlugin
from cfgnet.plugins.concept.circleci_plugin import CircleCiPlugin
from cfgnet.plugins.concept.cargo_plugin import CargoPlugin
from cfgnet.plugins.concept.github_actions_plugin import GitHubActionPlugin
from cfgnet.plugins.concept.gradle_plugin import GradlePlugin
from cfgnet.plugins.concept.flutter_plugin import FlutterPlugin
from cfgnet.plugins.concept.android_plugin import AndroidPlugin


class PluginManager:
    """Manager for plugin implementations."""

    concept_plugins: List[Plugin] = [
        DockerPlugin(),
        MavenPlugin(),
        NodejsPlugin(),
        CypressPlugin(),
        TsconfigPlugin(),
        DockerComposePlugin(),
        TravisPlugin(),
        PoetryPlugin(),
        SpringPlugin(),
        ApacheWebserverPlugin(),
        MysqlPlugin(),
        AnsiblePlugin(),
        AnsiblePlaybookPlugin(),
        PostgreSQLPlugin(),
        MongoDBPlugin(),
        DjangoPlugin(),
        ZookeeperPlugin(),
        AlluxioPlugin(),
        HadoopCommonPlugin(),
        HadoopHdfsPlugin(),
        HadoopHbasePlugin(),
        YarnPlugin(),
        ElasticsearchPlugin(),
        KafkaPlugin(),
        AngularPlugin(),
        MapReducePlugin(),
        CircleCiPlugin(),
        CargoPlugin(),
        GitHubActionPlugin(),
        GradlePlugin(),
        FlutterPlugin(),
        AndroidPlugin(),
    ]

    file_type_plugins: List[Plugin] = [
        ConfigParserPlugin(),
        YAMLPlugin(),
        TomlPlugin(),
        HadoopPlugin(),
    ]

    @staticmethod
    def get_plugins() -> List:
        """Return all plugins except vcs plugins."""
        return PluginManager.concept_plugins

    @staticmethod
    def get_responsible_plugin(
        plugins: List[Plugin], artifact_path: str
    ) -> Optional[Plugin]:
        """
        Identify plugin that is responsible for an artifact.

        :param artifact_path: Absolute path to the artifact
        :return: Responsible plugin or None if there is no such plugin
        """
        for plugin in plugins:
            if plugin.is_responsible(artifact_path):
                return plugin

        return None
