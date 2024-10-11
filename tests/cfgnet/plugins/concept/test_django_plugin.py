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

from cfgnet.plugins.concept.django_plugin import DjangoPlugin
from cfgnet.config_types.config_types import ConfigType
from tests.utility.id_creator import make_id


@pytest.fixture(name="get_plugin")
def get_plugin_():
    plugin = DjangoPlugin()
    return plugin


def test_is_responsible(get_plugin):
    django_plugin = get_plugin

    django_file = django_plugin.is_responsible(
        "tests/files/settings.py"
    )

    no_django_file = django_plugin.is_responsible(
        "tests/files/test.py"
    )

    assert django_file
    assert not no_django_file


def test_parse_django_file(get_plugin):
    django_plugin = get_plugin
    file = os.path.abspath("tests/files/settings.py")

    artifact = django_plugin.parse_file(file, "settings.py")
    nodes = artifact.get_nodes()
    ids = sorted(list({node.id for node in nodes}))

    assert len(nodes) == 16
    assert make_id("settings.py", "file", "settings.py") in ids
    assert make_id("settings.py", "DEBUG", "False") in ids
    assert make_id("settings.py", "ADMINS", "[]") in ids
    assert make_id("settings.py", "TIME_ZONE", "America/Chicago") in ids
    assert make_id("settings.py", "LANGUAGE_CODE", "en-us") in ids
    assert make_id("settings.py", "STORAGES", "default", "BACKEND", "django.core.files.storage.FileSystemStorage") in ids
    assert make_id("settings.py", "STORAGES", "staticfiles", "BACKEND", "django.contrib.staticfiles.storage.StaticFilesStorage") in ids
    assert make_id("settings.py", "FILE_UPLOAD_HANDLERS", "[django.core.files.uploadhandler.MemoryFileUploadHandler, django.core.files.uploadhandler.TemporaryFileUploadHandler]") in ids
    assert make_id("settings.py", "FILE_UPLOAD_MAX_MEMORY_SIZE", "2621440") in ids
    assert make_id("settings.py", "FILE_UPLOAD_DIRECTORY_PERMISSIONS", "None") in ids
    assert make_id("settings.py", "DATE_FORMAT", "N j, Y") in ids
    assert make_id("settings.py", "DEFAULT_AUTO_FIELD", "django.db.models.AutoField") in ids
    assert make_id("settings.py", "SESSION_COOKIE_AGE", "60 * 60 * 24 * 7 * 2") in ids
    assert make_id("settings.py", "AUTH_USER_MODEL", "auth.User") in ids
    assert make_id("settings.py", "LOGIN_URL", "/accounts/login/") in ids
    assert make_id("settings.py", "CSRF_COOKIE_PATH", "/") in ids


def test_django_config_types(get_plugin):
    django_plugin = get_plugin
    django_file = os.path.abspath("tests/files/settings.py")
    artifact = django_plugin.parse_file(django_file, "settings.py")
    nodes = artifact.get_nodes()

    url_node = next(filter(lambda x: x.id == make_id("settings.py", "LOGIN_URL", "/accounts/login/"), nodes))
    size_node = next(filter(lambda x: x.id == make_id("settings.py", "FILE_UPLOAD_MAX_MEMORY_SIZE", "2621440"), nodes))
    boolean_node = next(filter(lambda x: x.id == make_id("settings.py", "DEBUG", "False"), nodes))

    assert url_node.config_type == ConfigType.URL
    assert size_node.config_type == ConfigType.SIZE
    assert boolean_node.config_type == ConfigType.BOOLEAN
