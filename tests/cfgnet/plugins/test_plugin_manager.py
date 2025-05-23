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

from cfgnet.plugins.plugin_manager import PluginManager


def test_get_all_concept_plugins():
    all_concept_plugins = PluginManager.get_concept_plugins()

    assert len(all_concept_plugins) == 35


def test_get_responsible_concept_plugin():
    plugins = PluginManager.get_concept_plugins()

    docker_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/Dockerfile")
    maven_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/pom.xml")
    nodejs_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/package.json")
    docker_compose_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/docker-compose.yml")
    travis_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/.travis.yml")
    cypress_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/cypress.json")
    tsconfig_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/tsconfig.json")
    poetry_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/pyproject.toml")
    spring_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/application.properties")
    apache_webserver_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/httpd.conf")
    mysql_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/my.cnf")
    ansible_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/ansible.cfg")
    ansible_playbook_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/playbooks/test.yaml")
    postgresql_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/postgresql.conf")
    mongodb_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/mongod.conf")
    django_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/settings.py")
    zookeeper_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/zoo.cfg")
    alluxio_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/alluxio-site.properties")
    hadoop_common_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/core-site.xml")
    hadoop_hdfs_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/hdfs-site.xml")
    hadoop_hbase_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/hbase-site.xml")
    yarn_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/yarn-site.xml")
    elasticsearch_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/elasticsearch.yml")
    kafka_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/server.properties")
    angular_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/angular.json")
    mapreduce_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/mapred-site.xml")
    circleci_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/.circleci/config.yml")
    cargo_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/Cargo.toml")
    github_action_plugin = PluginManager.get_responsible_plugin(plugins, ".github/workflows/test.yml")
    gradle_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/gradle.properties")
    flutter_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/pubspec.yaml")
    android_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/AndroidManifest.xml")
    nginx_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/nginx.conf")
    redis_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/redis.conf")
    kubernetes_plugin = PluginManager.get_responsible_plugin(plugins, "path/to/deployment.yaml")

    assert docker_plugin.concept_name == "docker"
    assert maven_plugin.concept_name == "maven"
    assert nodejs_plugin.concept_name == "nodejs"
    assert docker_compose_plugin.concept_name == "docker-compose"
    assert travis_plugin.concept_name == "travis"
    assert cypress_plugin.concept_name == "cypress"
    assert tsconfig_plugin.concept_name == "tsconfig"
    assert poetry_plugin.concept_name == "poetry"
    assert spring_plugin.concept_name == "spring"
    assert apache_webserver_plugin.concept_name == "apache"
    assert mysql_plugin.concept_name == "mysql"
    assert ansible_plugin.concept_name == "ansible"
    assert ansible_playbook_plugin.concept_name == "ansible-playbook"
    assert postgresql_plugin.concept_name == "postgresql"
    assert mongodb_plugin.concept_name == "mongodb"
    assert django_plugin.concept_name == "django"
    assert zookeeper_plugin.concept_name == "zookeeper"
    assert alluxio_plugin.concept_name == "alluxio"
    assert hadoop_common_plugin.concept_name == "hadoop-common"
    assert hadoop_hdfs_plugin.concept_name == "hadoop-hdfs"
    assert hadoop_hbase_plugin.concept_name == "hadoop-hbase"
    assert yarn_plugin.concept_name == "yarn"
    assert elasticsearch_plugin.concept_name == "elasticsearch"
    assert kafka_plugin.concept_name == "kafka"
    assert angular_plugin.concept_name == "angular"
    assert mapreduce_plugin.concept_name == "mapreduce"
    assert circleci_plugin.concept_name == "circleci"
    assert cargo_plugin.concept_name == "cargo"
    assert github_action_plugin.concept_name == "github-action"
    assert gradle_plugin.concept_name == "gradle"
    assert flutter_plugin.concept_name == "flutter"
    assert android_plugin.concept_name == "android"
    assert nginx_plugin.concept_name == "nginx"
    assert redis_plugin.concept_name == "redis"
    assert kubernetes_plugin.concept_name == "kubernetes"
