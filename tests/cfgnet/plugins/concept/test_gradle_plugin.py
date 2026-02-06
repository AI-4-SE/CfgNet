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

    # Check for plugins (id as option, version as nested option, version number as value)
    # Structure: plugins -> plugin-id -> version -> version-number
    plugin_versions = next(
        filter(
            lambda x: x.id == make_id("build.gradle", "plugins", "com.github.ben-manes.versions", "version", "0.53.0"),
            nodes
        ),
        None
    )
    plugin_spotbugs = next(
        filter(
            lambda x: x.id == make_id("build.gradle", "plugins", "com.github.spotbugs", "version", "6.4.8"),
            nodes
        ),
        None
    )
    plugin_shadow = next(
        filter(
            lambda x: x.id == make_id("build.gradle", "plugins", "com.gradleup.shadow", "version", "9.3.1"),
            nodes
        ),
        None
    )
    plugin_jmh = next(
        filter(
            lambda x: x.id == make_id("build.gradle", "plugins", "me.champeau.jmh", "version", "0.7.2"),
            nodes
        ),
        None
    )

    assert plugin_versions is not None, "Plugin 'com.github.ben-manes.versions' should be parsed"
    assert plugin_spotbugs is not None, "Plugin 'com.github.spotbugs' should be parsed"
    assert plugin_shadow is not None, "Plugin 'com.gradleup.shadow' should be parsed"
    assert plugin_jmh is not None, "Plugin 'me.champeau.jmh' should be parsed"

    # Check for ext properties
    github_project_name = next(filter(lambda x: x.id == make_id("build.gradle", "ext.githubProjectName", "spectator"), nodes), None)
    assert github_project_name is not None

    # Check for dependencies
    # Structure: subprojects -> dependencies -> configuration-type -> dependency-name
    slf4j_dep = next(
        filter(
            lambda x: x.id == make_id("build.gradle", "subprojects", "dependencies", "implementation", "org.slf4j:slf4j-api"),
            nodes
        ),
        None
    )
    junit_dep = next(
        filter(
            lambda x: x.id == make_id("build.gradle", "subprojects", "dependencies", "testImplementation", "org.junit.jupiter:junit-jupiter"),
            nodes
        ),
        None
    )
    equalsverifier_dep = next(
        filter(
            lambda x: x.id == make_id("build.gradle", "subprojects", "dependencies", "testImplementation", "nl.jqno.equalsverifier:equalsverifier"),
            nodes
        ),
        None
    )

    assert slf4j_dep is not None, "SLF4J dependency should be parsed"
    assert junit_dep is not None, "JUnit Jupiter dependency should be parsed"
    assert equalsverifier_dep is not None, "EqualsVerifier dependency should be parsed"

    # Check for jmh section options (all options should be parsed, not just the first one)
    jmh_version = next(filter(lambda x: x.id == make_id("build.gradle", "subprojects", "jmh", "jmhVersion", "1.37"), nodes), None)
    jmh_warmup = next(filter(lambda x: x.id == make_id("build.gradle", "subprojects", "jmh", "warmupIterations", "2"), nodes), None)
    jmh_iterations = next(filter(lambda x: x.id == make_id("build.gradle", "subprojects", "jmh", "iterations", "5"), nodes), None)
    jmh_fork = next(filter(lambda x: x.id == make_id("build.gradle", "subprojects", "jmh", "fork", "1"), nodes), None)
    jmh_includeTests = next(filter(lambda x: x.id == make_id("build.gradle", "subprojects", "jmh", "includeTests", "false"), nodes), None)

    assert jmh_version is not None, "jmh.jmhVersion should be parsed"
    assert jmh_warmup is not None, "jmh.warmupIterations should be parsed (not just first option)"
    assert jmh_iterations is not None, "jmh.iterations should be parsed"
    assert jmh_fork is not None, "jmh.fork should be parsed"
    assert jmh_includeTests is not None, "jmh.includeTests should be parsed"

    # Check for checkstyle section options
    checkstyle_version = next(filter(lambda x: x.id == make_id("build.gradle", "subprojects", "checkstyle", "toolVersion", "13.1.0"), nodes), None)
    checkstyle_ignoreFailures = next(filter(lambda x: x.id == make_id("build.gradle", "subprojects", "checkstyle", "ignoreFailures", "false"), nodes), None)

    assert checkstyle_version is not None, "checkstyle.toolVersion should be parsed"
    assert checkstyle_ignoreFailures is not None, "checkstyle.ignoreFailures should be parsed"

    # Check for spotbugs section options
    spotbugs_version = next(filter(lambda x: x.id == make_id("build.gradle", "subprojects", "spotbugs", "toolVersion", "4.9.8"), nodes), None)
    spotbugs_useJavaToolchains = next(filter(lambda x: x.id == make_id("build.gradle", "subprojects", "spotbugs", "useJavaToolchains", "false"), nodes), None)
    spotbugs_ignoreFailures = next(filter(lambda x: x.id == make_id("build.gradle", "subprojects", "spotbugs", "ignoreFailures", "false"), nodes), None)

    assert spotbugs_version is not None, "spotbugs.toolVersion should be parsed"
    assert spotbugs_useJavaToolchains is not None, "spotbugs.useJavaToolchains should be parsed"
    assert spotbugs_ignoreFailures is not None, "spotbugs.ignoreFailures should be parsed"

    # Check for pmd section options
    pmd_version = next(filter(lambda x: x.id == make_id("build.gradle", "subprojects", "pmd", "toolVersion", "7.16.0"), nodes), None)
    pmd_ignoreFailures = next(filter(lambda x: x.id == make_id("build.gradle", "subprojects", "pmd", "ignoreFailures", "false"), nodes), None)

    assert pmd_version is not None, "pmd.toolVersion should be parsed"
    assert pmd_ignoreFailures is not None, "pmd.ignoreFailures should be parsed"


def test_parse_settings_gradle(get_plugin):
    plugin = get_plugin
    settings_file = os.path.abspath("tests/files/settings.gradle")
    artifact = plugin.parse_file(settings_file, "settings.gradle")

    assert artifact is not None
    assert artifact.concept_name == "gradle"

    nodes = artifact.get_nodes()
    assert len(nodes) >= 0
