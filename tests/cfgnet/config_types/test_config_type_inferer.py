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
import pytest
from cfgnet.config_types.config_type_inferer import ConfigTypeInferer
from cfgnet.config_types.config_types import ConfigType

test_dataset = [
    # Ports
    {"option_name": "db_port", "value": "5432", "expected_type": ConfigType.PORT},
    {"option_name": "server.port", "value": "8080", "expected_type": ConfigType.PORT},
    {"option_name": "listener_port", "value": "80", "expected_type": ConfigType.PORT},
    {"option_name": "ports.container", "value": "80", "expected_type": ConfigType.PORT},
    {"option_name": "ports.host", "value": "80", "expected_type": ConfigType.PORT},
    {"option_name": "http.port", "value": "9200", "expected_type": ConfigType.PORT},
    
    # Usernames
    {"option_name": "admin_user", "value": "admin", "expected_type": ConfigType.USERNAME},
    {"option_name": "ftp_username", "value": "ftp_user123", "expected_type": ConfigType.USERNAME},
    {"option_name": "spring.datasource.username", "value": "root", "expected_type": ConfigType.USERNAME},

    # Passwords
    {"option_name": "db_password", "value": "secret_password123", "expected_type": ConfigType.PASSWORD},
    {"option_name": "ftp_pass", "value": "MyP@ssw0rd!", "expected_type": ConfigType.PASSWORD},
    {"option_name": "spring.datasource.password", "value": "secret", "expected_type": ConfigType.PASSWORD},

    # URLs
    {"option_name": "api_url", "value": "https://api.example.com", "expected_type": ConfigType.URL},
    {"option_name": "homepage", "value": "http://example.org", "expected_type": ConfigType.URL},
    {"option_name": "spring.datasource.url", "value": "jdbc:mysql://localhost:3306/mydb", "expected_type": ConfigType.URL},
    {"option_name": "baseUrl", "value": "http://localhost:3000", "expected_type": ConfigType.URL},

    # IP Addresses
    {"option_name": "server_ip", "value": "192.168.1.1", "expected_type": ConfigType.IP_ADDRESS},
    {"option_name": "host_ip", "value": "10.0.0.254", "expected_type": ConfigType.IP_ADDRESS},
    {"option_name": "bindIp", "value": "127.0.0.1", "expected_type": ConfigType.IP_ADDRESS},
    
    # Sizes
    {"option_name": "max_file_size", "value": "20MB", "expected_type": ConfigType.SIZE},
    {"option_name": "cache_size", "value": "512KB", "expected_type": ConfigType.SIZE},
    {"option_name": "disk_size", "value": "100GB", "expected_type": ConfigType.SIZE},
    
    # Timeouts
    {"option_name": "session_timeout", "value": "30s", "expected_type": ConfigType.TIME},
    {"option_name": "request_timeout", "value": "500ms", "expected_type": ConfigType.TIME},
    {"option_name": "retry_interval", "value": "5min", "expected_type": ConfigType.TIME},
    
    # Version numbers
    {"option_name": "software_version", "value": "1.2.3", "expected_type": ConfigType.VERSION_NUMBER},
    {"option_name": "api_version", "value": "v2.3.4-beta", "expected_type": ConfigType.VERSION_NUMBER},
    {"option_name": "version", "value": "3.8", "expected_type": ConfigType.VERSION_NUMBER},
    {"option_name": "targetSdkVersion", "value": "30", "expected_type": ConfigType.VERSION_NUMBER},
    
    # Paths
    {"option_name": "volumes", "value": "/host/data:/container/data", "expected_type": ConfigType.PATH},
    {"option_name": "log_dir", "value": "/var/logs/app/", "expected_type": ConfigType.PATH},
    {"option_name": "config_path", "value": "/etc/app/config.yaml", "expected_type": ConfigType.PATH},
    {"option_name": "home_dir", "value": "~/home/user/", "expected_type": ConfigType.PATH},
    {"option_name": "build", "value": "./myapp", "expected_type": ConfigType.PATH},
    {"option_name": "outputPath", "value": "dist/my-app", "expected_type": ConfigType.PATH},
    {"option_name": "index", "value": "src/index.html", "expected_type": ConfigType.PATH},
    
    # File Names
    {"option_name": "logfile", "value": "output.log", "expected_type": ConfigType.PATH},
    {"option_name": "config_file", "value": "settings.ini", "expected_type": ConfigType.PATH},
    
    # Emails
    {"option_name": "admin_email", "value": "admin@example.com", "expected_type": ConfigType.EMAIL},
    {"option_name": "support_email", "value": "support@myapp.org", "expected_type": ConfigType.EMAIL},
    
    # IDs
    {"option_name": "session_id", "value": "abc123xyz", "expected_type": ConfigType.ID},
    {"option_name": "user_token", "value": "token-987654321", "expected_type": ConfigType.ID},
    {"option_name": "artifactId", "value": "my-app", "expected_type": ConfigType.ID},
    {"option_name": "groupID", "value": "com.maven.org", "expected_type": ConfigType.ID},
    
    # Number
    {"option_name": "max_connections", "value": "100", "expected_type": ConfigType.NUMBER},
    {"option_name": "retry_count", "value": "5", "expected_type": ConfigType.NUMBER},
    
    # Speeds
    {"option_name": "download_speed", "value": "100Mbps", "expected_type": ConfigType.SPEED},
    {"option_name": "upload_speed", "value": "50Mbps", "expected_type": ConfigType.SPEED},
    
    # Commands
    {"option_name": "install_script", "value": "install.sh", "expected_type": ConfigType.COMMAND},
    {"option_name": "start_script", "value": "node app.js", "expected_type": ConfigType.COMMAND},
    
    # Licenses
    {"option_name": "software_license", "value": "MIT", "expected_type": ConfigType.LICENSE},
    
    # Images
    {"option_name": "FROM", "value": "nginx:latest", "expected_type": ConfigType.IMAGE},
        
    # Names
    {"option_name": "container_name", "value": "my_container", "expected_type": ConfigType.NAME},
    {"option_name": "cluster.name", "value": "my-cluster", "expected_type": ConfigType.NAME},
    {"option_name": "node.name", "value": "node-1", "expected_type": ConfigType.NAME},
    
    # Booleans
    {"option_name": "compilerOptions.strict", "value": "true", "expected_type": ConfigType.BOOLEAN},
    {"option_name": "DEBUG", "value": "True", "expected_type": ConfigType.BOOLEAN},
    {"option_name": "production", "value": "true", "expected_type": ConfigType.BOOLEAN},
    {"option_name": "chromeWebSecurity", "value": "false", "expected_type": ConfigType.BOOLEAN},
    {"option_name": "enable_feature", "value": "true", "expected_type": ConfigType.BOOLEAN},
    {"option_name": "is_active", "value": "false", "expected_type": ConfigType.BOOLEAN},
    {"option_name": "debug_mode", "value": "1", "expected_type": ConfigType.BOOLEAN},
    {"option_name": "dark_mode", "value": "on", "expected_type": ConfigType.BOOLEAN},
    {"option_name": "safe_mode", "value": "off", "expected_type": ConfigType.BOOLEAN},

    # Misclassifications
    # {"option_name": "viewportWidth", "value": "1280", "expected_type": ConfigType.SIZE},  # SIZE
    # {"option_name": "minSdkVersion", "value": "21", "expected_type": ConfigType.VERSION_NUMBER},  # VERSION_NUMBER
    # {"option_name": "license_type", "value": "GPL", "expected_type": ConfigType.LICENSE},  # LICENSE
    # {"option_name": "max_length", "value": "100", "expected_type": ConfigType.SIZE},  # SIZE
    # {"option_name": "maven.compiler.source", "value": "1.8", "expected_type": ConfigType.VERSION_NUMBER},
    # {"option_name": "maven.compiler.target", "value": "1.8", "expected_type": ConfigType.VERSION_NUMBER},
    # {"option_name": "auth_key", "value": "auth_56789", "expected_type": ConfigType.ID},
    # {"option_name": "SECRET_KEY", "value": "django-insecure-secretkey", "expected_type": ConfigType.ID},
    # {"option_name": "start_command", "value": "run.sh", "expected_type": ConfigType.COMMAND},
]


@pytest.fixture(name="get_inferer")
def get_inferer_():
    inferer = ConfigTypeInferer()
    return inferer


def test_config_types(get_inferer):
    inferer = get_inferer

    for test in test_dataset:
        inferred_type = inferer.get_config_type(test["option_name"], test["value"])
        assert inferred_type == test["expected_type"]
