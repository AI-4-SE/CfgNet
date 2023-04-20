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

from cfgnet.plugins.concept.apache_webserver_plugin import ApacheWebserverPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = ApacheWebserverPlugin()
    return plugin


def test_is_responsible(get_plugin):
    apache_webserver_plugin = get_plugin

    apache_webserver_file = apache_webserver_plugin.is_responsible("/path/to/httpd.conf")
    not_apache_webserver_file = apache_webserver_plugin.is_responsible("/path/to/nothttpd.conf")

    assert apache_webserver_file
    assert not not_apache_webserver_file


def test_parse_apache_webserver_file(get_plugin):
    apache_webserver_plugin = get_plugin
    apache_webserver = os.path.abspath("tests/files/httpd.conf")

    artifact = apache_webserver_plugin.parse_file(apache_webserver, "httpd.conf")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 15

    assert make_id("httpd.conf", "file", "httpd.conf") in ids
    assert make_id("httpd.conf", "SSLCACertificatePath", "test.crt") in ids
    assert make_id("httpd.conf", "SSLCADNRequestFile", "test2.crt") in ids
    assert make_id("httpd.conf", "AccessFileName", ".htaccess") in ids
    assert make_id("httpd.conf", "AddLanguage", "ca .ca") in ids
    assert make_id("httpd.conf", "NameVirtualHost", "111.22.33.44") in ids

    assert make_id("httpd.conf", "IfModule", "mod_mime_magic.c", "MIMEMagicFile", "conf/magic") in ids
    assert make_id("httpd.conf", "IfModule", "mod_include.c", "Directory", "/var/www/error", "AllowOverride", "None") in ids
    assert make_id("httpd.conf", "IfModule", "mod_include.c", "Directory", "/var/www/error", "LanguagePriority", "en es de fr") in ids
    assert make_id("httpd.conf", "IfModule", "mod_include.c", "Directory", "/var/www/error", "ForceLanguagePriority", "Prefer Fallback") in ids

    assert make_id("httpd.conf", "VirtualHost", "10.1.2.3", "ServerAdmin", "test@uni-leipzig.de") in ids
    assert make_id("httpd.conf", "VirtualHost", "10.1.2.3", "DocumentRoot", "/var/www/html") in ids
    assert make_id("httpd.conf", "VirtualHost", "10.1.2.3", "ServerName", "test") in ids
    assert make_id("httpd.conf", "VirtualHost", "10.1.2.3", "ErrorLog", "error.log") in ids
    assert make_id("httpd.conf", "VirtualHost", "10.1.2.3", "TransferLog", "transfer.log") in ids


def test_config_types(get_plugin):
    apache_webserver_plugin = get_plugin
    apache_webserver = os.path.abspath("tests/files/httpd.conf")
    artifact = apache_webserver_plugin.parse_file(apache_webserver, "httpd.conf")
    nodes = artifact.get_nodes()

    admin = next(
        filter(
            lambda x: x.id == make_id("httpd.conf", "VirtualHost", "10.1.2.3", "ServerAdmin", "test@uni-leipzig.de"),
            nodes,
        )
    )
    root = next(
        filter(
            lambda x: x.id == make_id("httpd.conf", "VirtualHost", "10.1.2.3", "DocumentRoot", "/var/www/html"),
            nodes,
        )
    )
    access = next(
        filter(
            lambda x: x.id == make_id("httpd.conf", "AccessFileName", ".htaccess"),
            nodes,
        )
    )
    if_MIME = next(
        filter(
            lambda x: x.id == make_id("httpd.conf", "IfModule", "mod_mime_magic.c", "MIMEMagicFile", "conf/magic"),
            nodes,
        )
    )
    language1 = next(
        filter(
            lambda x: x.id == make_id("httpd.conf", "AddLanguage", "ca .ca"),
            nodes,
        )
    )

    path = next(
        filter(
            lambda x: x.id == make_id("httpd.conf", "SSLCACertificatePath", "test.crt"),
            nodes,
        )
    )

    ip_address = next(
        filter(
            lambda x: x.id == make_id("httpd.conf", "NameVirtualHost", "111.22.33.44"),
            nodes,
        )
    )
    assert admin.config_type == ConfigType.EMAIL
    assert root.config_type == ConfigType.PATH
    assert access.config_type == ConfigType.PATH
    assert if_MIME.config_type == ConfigType.PATH
    assert language1.config_type == ConfigType.LANGUAGE
    assert path.config_type == ConfigType.PATH
    assert ip_address.config_type == ConfigType.IP_ADDRESS
