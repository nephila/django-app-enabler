import json
import os
import sys
from importlib import import_module
from types import ModuleType
from unittest.mock import patch

from app_enabler.enable import _verify_settings, _verify_urlconf, apply_configuration_set, enable_application
from app_enabler.errors import messages
from tests.utils import working_directory


def test_enable(capsys, pytester, project_dir, addon_config, teardown_django):
    """Enabling application load the addon configuration in settings and urlconf."""

    with working_directory(project_dir), patch("app_enabler.enable.load_addon") as load_addon:
        del addon_config["settings"]["AUTH_PASSWORD_VALIDATORS"][-1]
        load_addon.return_value = addon_config
        os.environ["DJANGO_SETTINGS_MODULE"] = "test_project.settings"

        enable_application("djangocms_blog")

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

        enable_application("djangocms_blog")

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


def test_verify_fail(capsys, pytester, project_dir, addon_config_minimal, blog_package, teardown_django):
    """Enabling application load the addon configuration in settings and urlconf - minimal addon config."""

    with (
        working_directory(project_dir),
        patch("app_enabler.enable.load_addon") as load_addon,
        patch("app_enabler.enable.verify_installation") as verify_installation,
    ):
        load_addon.return_value = addon_config_minimal
        verify_installation.return_value = False
        os.environ["DJANGO_SETTINGS_MODULE"] = "test_project.settings"

        enable_application("djangocms_blog")

        captured = capsys.readouterr()
        assert captured.out == messages["verify_error"].format(package="djangocms-blog")


def test_enable_no_application(pytester, project_dir, addon_config, teardown_django):
    """Enabling application with empty addon configuration does not alter the configuration."""

    with working_directory(project_dir), patch("app_enabler.enable.load_addon") as load_addon:
        load_addon.return_value = None
        os.environ["DJANGO_SETTINGS_MODULE"] = "test_project.settings"

        enable_application("djangocms_blog")
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


def test_apply_configuration_set(capsys, pytester, project_dir, teardown_django):
    """Applying configurations from a list of json files update the project settings and urlconf."""

    with working_directory(project_dir):
        sample_config_set = [
            project_dir / "config" / "1.json",
            project_dir / "config" / "2.json",
            project_dir / "config" / "no_file.json",
        ]
        os.environ["DJANGO_SETTINGS_MODULE"] = "test_project.settings"

        json_configs = [json.loads(path.read_text()) for path in sample_config_set if path.exists()]

        apply_configuration_set(sample_config_set)

        captured = capsys.readouterr()
        assert "json1-a" in captured.out
        assert "json1-b" in captured.out
        assert "json2" in captured.out
        if os.environ["DJANGO_SETTINGS_MODULE"] in sys.modules:
            del sys.modules[os.environ["DJANGO_SETTINGS_MODULE"]]
        if "test_project.urls" in sys.modules:
            del sys.modules["test_project.urls"]
        imported_settings = import_module(os.environ["DJANGO_SETTINGS_MODULE"])
        imported_urls = import_module("test_project.urls")
        for config in json_configs:
            if not isinstance(config, list):
                config = [config]
            for item in config:
                assert _verify_settings(imported_settings, item)
                assert _verify_urlconf(imported_urls, item)
