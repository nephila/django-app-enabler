import os
import sys
from importlib import import_module
from types import ModuleType
from unittest.mock import patch

from app_enabler.enable import enable
from tests.test_patcher import check_settings_patched, check_urlconf_patched
from tests.utils import working_directory


def test_enable(pytester, project_dir, addon_config, teardown_django):
    """Executing setup_django will setup the corresponding django project."""

    with working_directory(project_dir), patch("app_enabler.enable.load_addon") as load_addon:
        load_addon.return_value = addon_config
        os.environ["DJANGO_SETTINGS_MODULE"] = "test_project.settings"
        if "test_project.settings" in sys.modules:
            del sys.modules["test_project.settings"]
        if "test_project.urls" in sys.modules:
            del sys.modules["test_project.urls"]

        enable("djangocms_blog")
        if "test_project.settings" in sys.modules:
            del sys.modules["test_project.settings"]
        if "test_project.urls" in sys.modules:
            del sys.modules["test_project.urls"]
        imported = import_module("test_project.settings")
        check_settings_patched(imported, addon_config)

        imported = import_module("test_project.urls")
        check_urlconf_patched(imported, addon_config)


def test_enable_no_application(pytester, project_dir, addon_config, teardown_django):
    """Executing setup_django will setup the corresponding django project."""

    with working_directory(project_dir), patch("app_enabler.enable.load_addon") as load_addon:
        load_addon.return_value = None
        os.environ["DJANGO_SETTINGS_MODULE"] = "test_project.settings"

        enable("djangocms_blog")
        if "test_project.settings" in sys.modules:
            del sys.modules["test_project.settings"]
        if "test_project.urls" in sys.modules:
            del sys.modules["test_project.urls"]
        imported = import_module("test_project.settings")
        assert "djangocms_blog" not in imported.INSTALLED_APPS
        assert "django.middleware.gzip.GZipMiddleware" not in imported.MIDDLEWARE

        imported = import_module("test_project.urls")
        urlpattern_patched = False
        for urlpattern in imported.urlpatterns:
            if (
                isinstance(urlpattern.urlconf_name, ModuleType)
                and urlpattern.urlconf_name.__name__ == "djangocms_blog.taggit_urls"
            ):
                urlpattern_patched = True
        assert not urlpattern_patched
