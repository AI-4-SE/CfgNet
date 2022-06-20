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

from cfgnet.config_types.config_types import ConfigType
from cfgnet.plugins.concept.spring_plugin import SpringPlugin
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = SpringPlugin()
    return plugin


def test_is_responsible(get_plugin):
    spring_plugin = get_plugin

    application_yml_file = spring_plugin.is_responsible(
        "tests/files/application.yml"
    )
    application_yml_dev_file = spring_plugin.is_responsible(
        "tests/files/application-dev.yml"
    )
    application_yml_prod_file = spring_plugin.is_responsible(
        "tests/files/application.prod.yml"
    )
    application_properties_file = spring_plugin.is_responsible(
        "tests/files/application.properties"
    )
    application_properties_dev_file = spring_plugin.is_responsible(
        "tests/files/application.prod.properties"
    )
    application_properties_prod_file = spring_plugin.is_responsible(
        "tests/files/application-dev.properties"
    )
    no_spring_file = spring_plugin.is_responsible("tests/files/test.yml")

    assert application_yml_file
    assert application_yml_prod_file
    assert application_yml_dev_file
    assert application_properties_file
    assert application_properties_dev_file
    assert application_properties_prod_file
    assert not no_spring_file


def test_parsing_spring_properties_file(get_plugin):
    spring_plugin = get_plugin
    file = os.path.abspath("tests/files/application.properties")

    artifact = spring_plugin.parse_file(file, "application.properties")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 12

    assert (
        make_id("application.properties", "file", "application.properties")
        in ids
    )
    assert make_id("application.properties", "server.port", "8090") in ids
    assert (
        make_id(
            "application.properties",
            "spring.datasource.url",
            "jdbc:h2:mem:blog_simple_db",
        )
        in ids
    )
    assert (
        make_id("application.properties", "spring.datasource.username", "sa")
        in ids
    )
    assert (
        make_id("application.properties", "spring.datasource.password", "abc")
        in ids
    )
    assert (
        make_id(
            "application.properties",
            "spring.datasource.data",
            "classpath:/sql/import-h2.sql",
        )
        in ids
    )
    assert (
        make_id("application.properties", "spring.h2.console.enabled", "true")
        in ids
    )
    assert (
        make_id(
            "application.properties", "spring.h2.console.path", "/h2-console"
        )
        in ids
    )
    assert (
        make_id("application.properties", "spring.admin.password", "admin")
        in ids
    )
    assert (
        make_id("application.properties", "spring.admin.password", "admin")
        in ids
    )
    assert (
        make_id("application.properties", "spring.thymeleaf.cache", "false")
        in ids
    )
    assert (
        make_id(
            "application.properties",
            "spring.thymeleaf.prefix",
            "classpath:/templates",
        )
        in ids
    )


def test_parsing_spring_yml_file(get_plugin):
    spring_plugin = get_plugin
    file = os.path.abspath("tests/files/application.yml")

    artifact = spring_plugin.parse_file(file, "application.yml")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 14

    assert make_id("application.yml", "file", "application.yml") in ids
    assert (
        make_id(
            "application.yml",
            "spring.datasource.url",
            "http://localhost:3306/",
        )
        in ids
    )
    assert (
        make_id(
            "application.yml", "spring.datasource.driver-class-name", "driver"
        )
        in ids
    )
    assert (
        make_id("application.yml", "spring.datasource.username", "dev") in ids
    )
    assert (
        make_id("application.yml", "spring.datasource.password", "dev") in ids
    )
    assert (
        make_id("application.yml", "spring.datasource.platform", "mysql")
        in ids
    )
    assert (
        make_id("application.yml", "spring.jpa.hibernate.ddl-auto", "validate")
        in ids
    )
    assert (
        make_id(
            "application.yml",
            "spring.jpa.database-platform",
            "org.hibernate.dialect",
        )
        in ids
    )
    assert make_id("application.yml", "spring.jpa.database", "mysql") in ids
    assert make_id("application.yml", "spring.jpa.show-sql", "True") in ids
    assert (
        make_id("application.yml", "default.admin.image", "admin.png") in ids
    )
    assert (
        make_id("application.yml", "default.admin.mail", "admin@mail.com")
        in ids
    )
    assert make_id("application.yml", "default.admin.name", "Admin") in ids
    assert make_id("application.yml", "default.admin.password", "1234") in ids


def yml_config_types(get_plugin):
    spring_plugin = get_plugin
    file = os.path.abspath("tests/files/application.yml")

    artifact = spring_plugin.parse_file(file, "application.yml")
    nodes = artifact.get_nodes()

    url_node = next(
        filter(
            lambda x: x.id
            == make_id(
                "application.yml",
                "spring.datasource.url",
                "http://localhost:3306/",
            ),
            nodes,
        )
    )
    username_node = next(
        filter(
            lambda x: x.id
            == make_id("application.yml", "spring.datasource.username", "dev"),
            nodes,
        )
    )
    password_node = next(
        filter(
            lambda x: x.id
            == make_id("application.yml", "spring.datasource.password", "dev"),
            nodes,
        )
    )

    assert url_node.config_type == ConfigType.URL
    assert username_node.config_type == ConfigType.USERNAME
    assert password_node.config_type == ConfigType.PASSWORD


def properties_config_types(get_plugin):
    spring_plugin = get_plugin
    file = os.path.abspath("tests/files/application.properties")

    artifact = spring_plugin.parse_file(file, "application.properties")
    nodes = artifact.get_nodes()

    port_node = next(
        filter(
            lambda x: x.id
            == make_id("application.properties", "server.port", "8090"),
            nodes,
        )
    )
    path_node = next(
        filter(
            lambda x: x.id
            == make_id(
                "application.properties",
                "spring.h2.console.path",
                "/h2-console",
            ),
            nodes,
        )
    )
    boolean_node = next(
        filter(
            lambda x: x.id
            == make_id(
                "application.properties", "spring.thymeleaf.cache", "false"
            ),
            nodes,
        )
    )

    assert port_node.config_type == ConfigType.PORT
    assert path_node.config_type == ConfigType.PATH
    assert boolean_node.config_type == ConfigType.BOOLEAN
