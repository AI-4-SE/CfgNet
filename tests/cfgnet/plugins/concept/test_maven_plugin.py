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

import pytest

from cfgnet.plugins.concept.maven_plugin import MavenPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = MavenPlugin()
    return plugin


def test_is_responsible(get_plugin):
    maven_plugin = get_plugin

    maven_file = maven_plugin.is_responsible("tests/files/pom.xml")
    not_maven_file = maven_plugin.is_responsible("tests/files/test.xml")

    assert maven_file
    assert not not_maven_file


def test_parse_file(get_plugin):
    maven_plugin = get_plugin
    maven_file = os.path.abspath("tests/files/pom.xml")
    artifact = maven_plugin.parse_file(maven_file, "pom.xml")

    value_nodes = artifact.get_nodes()
    ids = {node.id for node in value_nodes}

    for id in ids:
        print(id)

    assert artifact is not None
    assert len(value_nodes) == 33

    assert make_id("pom.xml", "project", "dependencyManagement", "dependencies", "dependency_hibernate", "version", "hibernate:3.2.5.ga") in ids
    assert make_id("pom.xml", "project", "dependencyManagement", "dependencies", "dependency_hibernate", "groupId", "org.hibernate") in ids
    assert make_id("pom.xml", "project", "dependencyManagement", "dependencies", "dependency_hibernate", "artifactId", "hibernate") in ids
    assert make_id("pom.xml", "project", "dependencyManagement", "dependencies", "dependency_ejb3-persistence", "version", "ejb3-persistence:1.0.1.GA") in ids
    assert make_id("pom.xml", "project", "dependencyManagement", "dependencies", "dependency_ejb3-persistence", "groupId", "org.hibernate") in ids
    assert make_id("pom.xml", "project", "dependencyManagement", "dependencies", "dependency_ejb3-persistence", "artifactId", "ejb3-persistence") in ids
    assert make_id("pom.xml", "project", "dependencyManagement", "dependencies", "dependency_hibernate-core", "version", "hibernate-core:3.6.3.Final") in ids
    assert make_id("pom.xml", "project", "dependencyManagement", "dependencies", "dependency_hibernate-core", "groupId", "org.hibernate") in ids
    assert make_id("pom.xml", "project", "dependencyManagement", "dependencies", "dependency_hibernate-core", "artifactId", "hibernate-core") in ids
    assert make_id("pom.xml", "project", "modules", "module", "config") in ids
    assert make_id("pom.xml", "project", "modelVersion", "modelVersion:4.0.0") in ids
    assert make_id("pom.xml", "project", "packaging", "jar") in ids
    assert make_id("pom.xml", "file", "pom.xml") in ids
    assert make_id("pom.xml", "project", "groupId", "com.example.apps") in ids
    assert make_id("pom.xml", "project", "artifactId", "my-cool-app") in ids
    assert make_id("pom.xml", "project", "version", "version:42") in ids
    assert make_id("pom.xml", "project", "packaging", "jar") in ids
    assert make_id("pom.xml", "ExecutableName", "target/my-cool-app-42.jar") in ids
    assert make_id("pom.xml", "ExecutableNameNoVersion", "target/my-cool-app.jar") in ids
    assert make_id("pom.xml", "project", "distributionManagement", "status", "deployed") in ids
    assert make_id("pom.xml", "project", "distributionManagement", "downloadUrl", "http://test/my-project") in ids
    assert make_id("pom.xml", "project", "issueManagement", "system", "Bugzilla") in ids
    assert make_id("pom.xml", "project", "issueManagement", "url", "http://test/bugzilla/") in ids
    assert make_id("pom.xml", "project", "build", "plugins", "plugin_maven-shade-plugin", "version", "maven-shade-plugin:1.4") in ids
    assert make_id("pom.xml", "project", "build", "plugins", "plugin_maven-shade-plugin", "groupId", "org.apache.maven.plugins") in ids
    assert make_id("pom.xml", "project", "build", "plugins", "plugin_maven-shade-plugin", "artifactId", "maven-shade-plugin") in ids
    assert make_id("pom.xml", "project", "build", "plugins", "plugin_maven-shade-plugin", "executions", "execution", "phase", "package") in ids
    assert make_id("pom.xml", "project", "build", "plugins", "plugin_maven-shade-plugin", "configuration", "finalName", "test") in ids
    assert make_id("pom.xml", "project", "build", "plugins", "plugin_maven-shade-plugin", "executions", "execution", "goals", "goal_shade", "shade") in ids
    assert make_id("pom.xml", "project", "build", "plugins", "plugin_maven-compiler-plugin", "version", "maven-compiler-plugin:2.3.2") in ids
    assert make_id("pom.xml", "project", "build", "plugins", "plugin_maven-compiler-plugin", "groupId", "org.apache.maven.plugins") in ids
    assert make_id("pom.xml", "project", "build", "plugins", "plugin_maven-compiler-plugin", "artifactId", "maven-compiler-plugin") in ids
    assert make_id("pom.xml", "project", "build", "plugins", "plugin_maven-compiler-plugin", "configuration", "source", "source:1.6") in ids
    assert make_id("pom.xml", "project", "build", "plugins", "plugin_maven-compiler-plugin", "configuration", "target", "target:1.6") in ids


def test_config_types(get_plugin):
    maven_plugin = get_plugin
    maven_file = os.path.abspath("tests/files/pom.xml")
    artifact = maven_plugin.parse_file(maven_file, "pom.xml")
    nodes = artifact.get_nodes()

    artifactId_node = next(
        filter(
            lambda x: x.id
            == make_id(
                "pom.xml",
                "project",
                "artifactId",
                "my-cool-app",
            ),
            nodes,
        )
    )
    executable_name = next(
        filter(
            lambda x: x.id
            == make_id(
                "pom.xml",
                "ExecutableName",
                "target/my-cool-app-42.jar",
            ),
            nodes,
        )
    )
    executable_name_no_version = next(
        filter(
            lambda x: x.id
            == make_id(
                "pom.xml", "ExecutableNameNoVersion", "target/my-cool-app.jar"
            ),
            nodes,
        )
    )

    version_node = next(
        filter(
            lambda x: x.id
            == make_id("pom.xml", "project", "version", "version:42"),
            nodes,
        )
    )

    modelVersion_node = next(
        filter(
            lambda x: x.id
            == make_id(
                "pom.xml", "project", "modelVersion", "modelVersion:4.0.0"
            ),
            nodes,
        )
    )

    assert artifactId_node.config_type == ConfigType.NAME
    assert executable_name.config_type == ConfigType.PATH
    assert executable_name_no_version.config_type == ConfigType.PATH
    assert version_node.config_type == ConfigType.VERSION_NUMBER
    assert modelVersion_node.config_type == ConfigType.VERSION_NUMBER
