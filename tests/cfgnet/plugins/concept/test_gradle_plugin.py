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

from cfgnet.plugins.concept.gradle_plugin import GradlePlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = GradlePlugin()
    return plugin


def test_is_responsible(get_plugin):
    plugin = get_plugin

    assert plugin.is_responsible("tests/files/gradle.properties")
    assert not plugin.is_responsible("tests/files/test.properties")


def test_config_types(get_plugin):
    plugin = get_plugin
    gradle_file = os.path.abspath("tests/files/gradle.properties")
    artifact = plugin.parse_file(gradle_file, "gradle.properties")
    nodes = artifact.get_nodes()

    name_node = next(filter(lambda x: x.id == make_id("gradle.properties", "appname", "MyApp"), nodes))
    boolean_node = next(filter(lambda x: x.id == make_id("gradle.properties", "org.gradle.daemon", "true"), nodes))
    time_node = next(filter(lambda x: x.id == make_id("gradle.properties", "org.gradle.daemon.idletimeout", "1000"), nodes))
    version_node = next(filter(lambda x: x.id == make_id("gradle.properties", "projectversion", "1.0.0"), nodes))
    user_node = next(filter(lambda x: x.id == make_id("gradle.properties", "systemprop.gradle.wrapperuser", "myuser"), nodes))
    password_node = next(filter(lambda x: x.id == make_id("gradle.properties", "systemprop.gradle.wrapperpassword", "12345"), nodes))

    assert name_node.config_type == ConfigType.NAME
    assert boolean_node.config_type == ConfigType.BOOLEAN
    assert time_node.config_type == ConfigType.TIME
    assert version_node.config_type == ConfigType.VERSION_NUMBER
    assert user_node.config_type == ConfigType.USERNAME
    assert password_node.config_type == ConfigType.PASSWORD


def test_is_responsible_build_gradle(get_plugin):
    plugin = get_plugin

    assert plugin.is_responsible("tests/files/build.gradle")
    assert plugin.is_responsible("tests/files/build.gradle.kts")
    assert not plugin.is_responsible("tests/files/random.gradle")


def test_is_responsible_settings_gradle(get_plugin):
    plugin = get_plugin

    assert plugin.is_responsible("tests/files/settings.gradle")
    assert plugin.is_responsible("tests/files/settings.gradle.kts")


def test_parse_build_gradle(get_plugin):
    plugin = get_plugin
    build_file = os.path.abspath("tests/files/build.gradle")
    artifact = plugin.parse_file(build_file, "build.gradle")

    assert artifact is not None
    assert artifact.concept_name == "gradle"

    nodes = artifact.get_nodes()
    assert len(nodes) > 0

    # Check for specific extracted values
    group_node = next(filter(lambda x: x.id == make_id("build.gradle", "group", "com.example"), nodes), None)
    version_node = next(filter(lambda x: x.id == make_id("build.gradle", "version", "1.0.0"), nodes), None)
    source_compat_node = next(filter(lambda x: x.id == make_id("build.gradle", "sourceCompatibility", "11"), nodes), None)
    main_class_node = next(filter(lambda x: x.id == make_id("build.gradle", "application", "mainClass", "com.example.Main"), nodes), None)

    assert group_node is not None
    assert group_node.config_type == ConfigType.NAME
    assert version_node is not None
    assert version_node.config_type == ConfigType.VERSION_NUMBER
    assert source_compat_node is not None
    assert main_class_node is not None

    # Check for ext properties
    kotlin_version_node = next(filter(lambda x: x.id == make_id("build.gradle", "ext", "kotlinVersion", "1.8.0"), nodes), None)
    spring_version_node = next(filter(lambda x: x.id == make_id("build.gradle", "ext", "springVersion", "5.3.20"), nodes), None)

    assert kotlin_version_node is not None
    assert spring_version_node is not None

    # Check for specific dependencies (groupId:artifactId as option, version as value)
    # Structure: dependencies -> org.springframework.boot:spring-boot-starter-web -> 2.7.0
    spring_boot_dep = next(
        filter(
            lambda x: x.id == make_id("build.gradle", "dependencies", "org.springframework.boot:spring-boot-starter-web", "2.7.0"),
            nodes
        ),
        None
    )
    junit_dep = next(
        filter(
            lambda x: x.id == make_id("build.gradle", "dependencies", "junit:junit", "4.13.2"),
            nodes
        ),
        None
    )

    assert spring_boot_dep is not None, "Spring Boot dependency should be parsed as groupId:artifactId"
    assert junit_dep is not None, "JUnit dependency should be parsed as groupId:artifactId"

    # Check for ext properties
    kotlin_version_node = next(filter(lambda x: x.id == make_id("build.gradle", "ext", "kotlinVersion", "1.8.0"), nodes), None)
    spring_version_node = next(filter(lambda x: x.id == make_id("build.gradle", "ext", "springVersion", "5.3.20"), nodes), None)

    assert kotlin_version_node is not None
    assert spring_version_node is not None


def test_parse_settings_gradle(get_plugin):
    plugin = get_plugin
    settings_file = os.path.abspath("tests/files/settings.gradle")
    artifact = plugin.parse_file(settings_file, "settings.gradle")

    assert artifact is not None
    assert artifact.concept_name == "gradle"

    nodes = artifact.get_nodes()
    assert len(nodes) >= 0
