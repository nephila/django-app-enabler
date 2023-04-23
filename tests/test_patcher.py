import ast
import os
import sys
import warnings
from importlib import import_module

import astor
import pytest
from django.urls import LocalePrefixPattern, URLPattern, URLResolver

from app_enabler.enable import _verify_settings, _verify_urlconf
from app_enabler.errors import messages
from app_enabler.patcher import setup_django, update_setting, update_urlconf
from tests.utils import working_directory


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
    """Project settings is patched with data from addon configuration."""
    settings_file = project_dir / "test_project" / "settings.py"

    update_setting(settings_file, addon_config)
    sys.path.insert(0, str(settings_file.parent))
    imported = import_module("settings")
    with warnings.catch_warnings(record=True) as w:
        # settings is not verified as BotchedCommonPasswordValidator is not added, this is expected and tested
        assert _verify_settings(imported, addon_config) is False
        assert len(w) == 1
        assert issubclass(w[-1].category, RuntimeWarning)
        assert "Configuration error for AUTH_PASSWORD_VALIDATORS" in str(w[-1].message)
    assert imported.MIDDLEWARE.index("django.middleware.common.CommonMiddleware") > imported.MIDDLEWARE.index(
        "django.middleware.locale.LocaleMiddleware"
    )
    assert imported.MIDDLEWARE.index("django.middleware.http.ConditionalGetMiddleware") == 2
    assert (
        imported.AUTH_PASSWORD_VALIDATORS[0]["NAME"]
        == "django.contrib.auth.password_validation.SuperCommonPasswordValidator"
    )
    assert (
        imported.AUTH_PASSWORD_VALIDATORS[2]["NAME"]
        == "django.contrib.auth.password_validation.NumericPasswordValidator"
    )
    assert "django.contrib.auth.password_validation.BotchedCommonPasswordValidator" not in [
        item["NAME"] for item in imported.AUTH_PASSWORD_VALIDATORS
    ]
    assert imported.INSTALLED_APPS.index("taggit") == imported.INSTALLED_APPS.index("taggit_autosuggest") + 1
    assert imported.INSTALLED_APPS.index("aldryn_apphooks_config") == 0


def test_update_urlconf(pytester, django_setup, project_dir, addon_config):
    """Project urlconf is patched with data from addon configuration."""
    urlconf_file = project_dir / "test_project" / "urls.py"

    update_urlconf(urlconf_file, addon_config)
    sys.path.insert(0, str(urlconf_file.parent))
    imported = import_module("urls")
    assert _verify_urlconf(imported, addon_config)


def test_update_urlconf_multiple_include(pytester, django_setup, project_dir, addon_config):
    """Repeated calls to update_urlconf only add a single include."""
    urlconf_file = project_dir / "test_project" / "urls.py"

    update_urlconf(urlconf_file, addon_config)
    update_urlconf(urlconf_file, addon_config)
    update_urlconf(urlconf_file, addon_config)

    parsed = astor.parse_file(urlconf_file)
    for node in parsed.body:
        if isinstance(node, ast.ImportFrom) and node.module == "django.urls":
            assert len(node.names) == 2
            assert "path" in (alias.name for alias in node.names)
            assert "include" in (alias.name for alias in node.names)


def test_update_urlconf_multiple_urlconf(pytester, django_setup, project_dir, addon_config):
    """Repeated calls to update_urlconf only add a single application urlconf instance."""
    urlconf_file = project_dir / "test_project" / "urls.py"

    update_urlconf(urlconf_file, addon_config)
    update_urlconf(urlconf_file, addon_config)
    update_urlconf(urlconf_file, addon_config)

    imported_urlconf = import_module("test_project.urls")
    instances_admin = 0
    instances_blog = 0
    instances_i18n = 0
    instances_view = 0
    instances_sitemap = 0
    for pattern in imported_urlconf.urlpatterns:
        if isinstance(pattern, URLResolver):
            if isinstance(pattern.urlconf_module, list):
                if pattern.app_name == "admin":
                    instances_admin += 1
                elif isinstance(pattern.pattern, LocalePrefixPattern):
                    instances_i18n += 1
            elif pattern.urlconf_module.__name__ == "djangocms_blog.taggit_urls":
                instances_blog += 1
        elif isinstance(pattern, URLPattern):
            if pattern.lookup_str == "django.contrib.sitemaps.views.sitemap":
                instances_sitemap += 1
            elif pattern.lookup_str == "django.views.generic.base.View":
                instances_view += 1
    assert instances_admin == 1
    assert instances_blog == 1
    assert instances_i18n == 1
    assert instances_view == 1
    assert instances_sitemap == 1
