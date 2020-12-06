import os
import sys
from importlib import import_module
from types import ModuleType
from typing import Any, Dict

import pytest
from django.conf import LazySettings

from app_enabler.errors import messages
from app_enabler.patcher import setup_django, update_setting, update_urlconf
from tests.utils import working_directory


def check_settings_patched(imported: LazySettings, addon_config: Dict[str, Any]):
    """Assert that addon config has been properly set in patched settings."""

    for app in addon_config["installed-apps"]:
        assert app in imported.INSTALLED_APPS
    assert imported.META_SITE_PROTOCOL == "https"
    assert imported.META_USE_SITES is True
    assert "django.middleware.gzip.GZipMiddleware" in imported.MIDDLEWARE


def check_urlconf_patched(imported: ModuleType, addon_config: Dict[str, Any]):
    """Assert that addon urlconf has been properly added in patched urlconf."""

    # as we want to make sure urlpatterns is really tested, we check both that an existing module of the correct type
    # is the module from addon config, and that the assert is reached for real
    urlpatterns_checked = False
    # include function is added by our patcher, soo we must ensure it is available
    assert imported.include
    for urlpattern in imported.urlpatterns:
        if isinstance(urlpattern.urlconf_name, ModuleType):
            urlpatterns_checked = True
            assert urlpattern.urlconf_name.__name__ == "djangocms_blog.taggit_urls"
    assert urlpatterns_checked


def test_setup_django_no_manage(capsys, project_dir, teardown_django):
    """Executing setup_django outside a project root raise a specific exception."""
    from django.apps import apps

    apps.ready = False
    apps.loading = False
    apps.app_configs = {}

    with working_directory(project_dir / "test_project"):
        os.environ["DJANGO_SETTINGS_MODULE"] = "test_project.settings"
        with pytest.raises(SystemExit):
            setup_django()

        assert not apps.ready
        captured = capsys.readouterr()
        assert captured.err.strip() == messages["no_managepy"].strip()


def test_setup_django(project_dir, teardown_django):
    """Executing setup_django will setup the corresponding django project."""
    from django.apps import apps

    with working_directory(project_dir):
        os.environ["DJANGO_SETTINGS_MODULE"] = "test_project.settings"
        setup_django()
        assert apps.ready
        assert len(apps.get_app_configs()) == 6


def test_update_setting(pytester, project_dir, addon_config):
    """ Project settings is patched with data from addon configuration. """
    settings_file = project_dir / "test_project" / "settings.py"

    update_setting(settings_file, addon_config)
    sys.path.insert(0, str(settings_file.parent))
    imported = import_module("settings")
    check_settings_patched(imported, addon_config)


def test_update_urlconf(pytester, django_setup, project_dir, addon_config):
    """ Project urlconf is patched with data from addon configuration. """
    urlconf_file = project_dir / "test_project" / "urls.py"

    update_urlconf(urlconf_file, addon_config)
    sys.path.insert(0, str(urlconf_file.parent))
    imported = import_module("urls")
    check_urlconf_patched(imported, addon_config)
