import os
import sys
from importlib import import_module

import pytest

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
    """ Project settings is patched with data from addon configuration. """
    settings_file = project_dir / "test_project" / "settings.py"

    update_setting(settings_file, addon_config)
    sys.path.insert(0, str(settings_file.parent))
    imported = import_module("settings")
    assert _verify_settings(imported, addon_config)


def test_update_urlconf(pytester, django_setup, project_dir, addon_config):
    """ Project urlconf is patched with data from addon configuration. """
    urlconf_file = project_dir / "test_project" / "urls.py"

    update_urlconf(urlconf_file, addon_config)
    sys.path.insert(0, str(urlconf_file.parent))
    imported = import_module("urls")
    assert _verify_urlconf(imported, addon_config)
