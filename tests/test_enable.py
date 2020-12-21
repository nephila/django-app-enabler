import os
import sys
from importlib import import_module
from types import ModuleType
from unittest.mock import patch

from app_enabler.enable import _verify_settings, _verify_urlconf, enable
from tests.utils import working_directory


def test_enable(capsys, pytester, project_dir, addon_config, teardown_django):
    """Enabling application load the addon configuration in settings and urlconf."""

    with working_directory(project_dir), patch("app_enabler.enable.load_addon") as load_addon:
        load_addon.return_value = addon_config
        os.environ["DJANGO_SETTINGS_MODULE"] = "test_project.settings"

        enable("djangocms_blog")

        captured = capsys.readouterr()
        assert addon_config["message"] in captured.out
        if os.environ["DJANGO_SETTINGS_MODULE"] in sys.modules:
            del sys.modules[os.environ["DJANGO_SETTINGS_MODULE"]]
        if "test_project.urls" in sys.modules:
            del sys.modules["test_project.urls"]
        imported = import_module(os.environ["DJANGO_SETTINGS_MODULE"])
        assert _verify_settings(imported, addon_config)

        imported = import_module("test_project.urls")
        assert _verify_urlconf(imported, addon_config)


def test_enable_minimal(capsys, pytester, project_dir, addon_config_minimal, teardown_django):
    """Enabling application load the addon configuration in settings and urlconf - minimal addon config."""

    with working_directory(project_dir), patch("app_enabler.enable.load_addon") as load_addon:
        load_addon.return_value = addon_config_minimal
        os.environ["DJANGO_SETTINGS_MODULE"] = "test_project.settings"

        enable("djangocms_blog")

        captured = capsys.readouterr()
        assert not captured.out
        if os.environ["DJANGO_SETTINGS_MODULE"] in sys.modules:
            del sys.modules[os.environ["DJANGO_SETTINGS_MODULE"]]
        if "test_project.urls" in sys.modules:
            del sys.modules["test_project.urls"]
        imported = import_module(os.environ["DJANGO_SETTINGS_MODULE"])
        assert _verify_settings(imported, addon_config_minimal)

        imported = import_module("test_project.urls")
        assert _verify_urlconf(imported, addon_config_minimal)


def test_enable_no_application(pytester, project_dir, addon_config, teardown_django):
    """Enabling application with empty addon configuration does not alter the configuration."""

    with working_directory(project_dir), patch("app_enabler.enable.load_addon") as load_addon:
        load_addon.return_value = None
        os.environ["DJANGO_SETTINGS_MODULE"] = "test_project.settings"

        enable("djangocms_blog")
        if os.environ["DJANGO_SETTINGS_MODULE"] in sys.modules:
            del sys.modules[os.environ["DJANGO_SETTINGS_MODULE"]]
        if "test_project.urls" in sys.modules:
            del sys.modules["test_project.urls"]
        imported = import_module(os.environ["DJANGO_SETTINGS_MODULE"])
        assert "djangocms_blog" not in imported.INSTALLED_APPS
        assert "django.middleware.gzip.GZipMiddleware" not in imported.MIDDLEWARE

        imported = import_module("test_project.urls")
        urlpattern_patched = False
        for urlpattern in imported.urlpatterns:
            if (
                getattr(urlpattern, "urlconf_name", None)
                and isinstance(urlpattern.urlconf_name, ModuleType)
                and urlpattern.urlconf_name.__name__ == "djangocms_blog.taggit_urls"
            ):
                urlpattern_patched = True
        assert not urlpattern_patched
