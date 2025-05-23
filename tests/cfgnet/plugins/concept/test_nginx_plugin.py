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

from cfgnet.plugins.concept.nginx_plugin import NginxPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


def test_is_responsible():
    """Test if the plugin is responsible for the given file."""
    plugin = NginxPlugin()

    assert plugin.is_responsible("path/to/nginx.conf")
    assert not plugin.is_responsible("path/to/other.conf")


def test_get_config_type():
    """Test configuration type inference."""
    plugin = NginxPlugin()

    assert plugin.get_config_type("listen") == ConfigType.PORT
    assert plugin.get_config_type("server_name") == ConfigType.NAME
    assert plugin.get_config_type("root") == ConfigType.PATH
    assert plugin.get_config_type("client_max_body_size") == ConfigType.SIZE
    assert plugin.get_config_type("proxy_read_timeout") == ConfigType.TIME
    assert plugin.get_config_type("proxy_pass") == ConfigType.URL
    assert plugin.get_config_type("ssl_protocols") == ConfigType.TYPE
    assert plugin.get_config_type("auth_basic") == ConfigType.PASSWORD


def test_parse_config_file(tmp_path):
    """Test parsing of Nginx configuration file."""
    plugin = NginxPlugin()
    nginx_file = "tests/files/nginx.conf"
    artifact = plugin.parse_file(nginx_file, "nginx.conf")
    nodes = artifact.get_nodes()
    ids = {node.id for node in nodes}

    assert artifact is not None
    assert len(nodes) == 33

    assert make_id("nginx.conf", "file", "nginx.conf") in ids
    assert make_id("nginx.conf", "user", "nginx") in ids
    assert make_id("nginx.conf", "worker_processes", "auto") in ids
    assert make_id("nginx.conf", "error_log", "/var/log/nginx/error.log") in ids
    assert make_id("nginx.conf", "pid", "/run/nginx.pid") in ids
    assert make_id("nginx.conf", "events", "worker_connections", "1024") in ids
    assert make_id("nginx.conf", "http", "include", "/etc/nginx/mime.types") in ids
    assert make_id("nginx.conf", "http", "default_type", "application/octet-stream") in ids

    assert make_id("nginx.conf", "http", "access_log", "/var/log/nginx/access.log main") in ids
    assert make_id("nginx.conf", "http", "sendfile", "on") in ids
    assert make_id("nginx.conf", "http", "tcp_nopush", "on") in ids
    assert make_id("nginx.conf", "http", "tcp_nodelay", "on") in ids
    assert make_id("nginx.conf", "http", "keepalive_timeout", "65") in ids
    assert make_id("nginx.conf", "http", "types_hash_max_size", "2048") in ids

    assert make_id("nginx.conf", "http", "server", "server_name", "example.com") in ids
    assert make_id("nginx.conf", "http", "server", "listen", "80") in ids
    assert make_id("nginx.conf", "http", "server", "server_name", "example.com") in ids
    assert make_id("nginx.conf", "http", "server", "root", "/var/www/html") in ids
    assert make_id("nginx.conf", "http", "server", "location /", "try_files", "$uri $uri/ /index.html") in ids

    assert make_id("nginx.conf", "http", "server", "location /api", "proxy_pass", "http://backend:8080") in ids
    assert make_id("nginx.conf", "http", "server", "location /api", "proxy_set_header", "Host $host") in ids
    assert make_id("nginx.conf", "http", "server", "location /api", "proxy_set_header", "X-Real-IP $remote_addr") in ids
    assert make_id("nginx.conf", "http", "server", "location /api", "proxy_read_timeout", "60s") in ids
    assert make_id("nginx.conf", "http", "server", "location /api", "proxy_connect_timeout", "60s") in ids

    assert make_id("nginx.conf", "http", "server", "location /static", "alias", "/var/www/static") in ids
    assert make_id("nginx.conf", "http", "server", "location /static", "expires", "30d") in ids
    assert make_id("nginx.conf", "http", "server", "location /static", "add_header", 'Cache-Control "public, no-transform"') in ids

    assert make_id("nginx.conf", "http", "server", "client_max_body_size", "10M") in ids
    assert make_id("nginx.conf", "http", "server", "ssl_protocols", "TLSv1.2 TLSv1.3") in ids
    assert make_id("nginx.conf", "http", "server", "ssl_ciphers", "HIGH:!aNULL:!MD5") in ids
    assert make_id("nginx.conf", "http", "server", "ssl_certificate", "/etc/nginx/ssl/example.com.crt") in ids
    assert make_id("nginx.conf", "http", "server", "ssl_certificate_key", "/etc/nginx/ssl/example.com.key") in ids
    assert make_id("nginx.conf", "http", "server", "auth_basic", '"Restricted Area"') in ids
    assert make_id("nginx.conf", "http", "server", "auth_basic_user_file", "/etc/nginx/.htpasswd") in ids
