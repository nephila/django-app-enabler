import json
import sys
import warnings
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List

import django.conf

from .django import get_settings_path, get_urlconf_path, load_addon
from .errors import messages
from .patcher import setup_django, update_setting, update_urlconf


def _verify_settings(imported: ModuleType, application_config: Dict[str, Any]) -> bool:
    """
    Check that addon config has been properly set in patched settings.

    :param ModuleType imported:  Update settings module
    :param dict application_config: addon configuration
    """

    def _validate_setting(key: str, value: Any):
        """
        Validate the given value for a single setting.

        It's aware of the possible structures of the application config setting (either a literal or a dict with the
        precedence information).
        """
        passed = True
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    real_item = item["value"]
                    passed = passed and (real_item in getattr(imported, key))
                    if not passed:  # pragma: no cover
                        warnings.warn(f"Configuration error for {key}", RuntimeWarning)
                else:
                    passed = passed and (item in getattr(imported, key))
                    if not passed:  # pragma: no cover
                        warnings.warn(f"Configuration error for {key}", RuntimeWarning)
        else:
            passed = passed and getattr(imported, key) == value
            if not passed:  # pragma: no cover
                warnings.warn(f"Configuration error for {key}", RuntimeWarning)
        return passed

    test_passed = _validate_setting("INSTALLED_APPS", application_config.get("installed-apps", []))
    for setting_name, setting_value in application_config.get("settings", {}).items():
        test_passed = test_passed and _validate_setting(setting_name, setting_value)
    return test_passed


def _verify_urlconf(imported: ModuleType, application_config: Dict[str, Any]) -> bool:
    """
    Check that addon urlconf has been properly added in patched urlconf.


    :param ModuleType imported: Update ``ROOT_URLCONF`` module
    :param dict application_config: addon configuration
    """
    # include function is added by our patcher, soo we must ensure it is available
    test_passed = bool(imported.include)
    included_urls = [url[1] for url in application_config.get("urls", [])]
    # as we want to make sure urlpatterns is really tested, we check both that an existing module of the correct type
    # is the module from addon config, and that the assert is reached for real
    urlpatterns_checked = not included_urls
    if included_urls:
        for urlpattern in imported.urlpatterns:
            try:
                if isinstance(urlpattern.urlconf_name, ModuleType):
                    urlpatterns_checked = True
                    test_passed = test_passed and urlpattern.urlconf_name.__name__ in included_urls
            except AttributeError:
                pass
    return test_passed and urlpatterns_checked


def verify_installation(settings: django.conf.LazySettings, application_config: Dict[str, Any]) -> bool:
    """
    Verify that package installation has been successful.

    :param django.conf.LazySettings settings: Path to settings file
    :param dict application_config: addon configuration
    """
    try:
        del sys.modules[settings.SETTINGS_MODULE]
    except KeyError:  # pragma: no cover
        pass
    try:
        del sys.modules[settings.ROOT_URLCONF]
    except KeyError:  # pragma: no cover
        pass
    imported_settings = import_module(settings.SETTINGS_MODULE)
    imported_urlconf = import_module(settings.ROOT_URLCONF)
    test_passed = _verify_settings(imported_settings, application_config)
    test_passed = test_passed and _verify_urlconf(imported_urlconf, application_config)
    return test_passed


def output_message(message: str):
    """
    Print the given message to stdout.

    :param str message: Success message to display
    """
    if message:
        sys.stdout.write(message)


def apply_configuration(application_config: Dict[str, Any]):
    """
    Enable django application in the current project

    :param dict application_config: addon configuration
    """

    setting_file = get_settings_path(django.conf.settings)
    urlconf_file = get_urlconf_path(django.conf.settings)
    update_setting(setting_file, application_config)
    update_urlconf(urlconf_file, application_config)
    if verify_installation(django.conf.settings, application_config):
        output_message(application_config.get("message", ""))
    else:
        output_message(messages["verify_error"].format(package=application_config.get("package-name")))


def enable_application(application: str, verbose: bool = False):
    """
    Enable django application in the current project

    :param str application: python module name to enable. It must be the name of a Django application.
    :param bool verbose: Verbose output (currently unused)
    """
    setup_django()

    application_config = load_addon(application)
    if application_config:
        apply_configuration(application_config)


def apply_configuration_set(config_set: List[Path], verbose: bool = False):
    """
    Apply settings from the list of input files.

    :param list config_set: list of paths to addon configuration to load and apply
    :param bool verbose: Verbose output (currently unused)
    """
    setup_django()

    for config_path in config_set:
        try:
            config_data = json.loads(config_path.read_text())
        except OSError:
            config_data = []
        if config_data:
            if not isinstance(config_data, list):
                config_data = [config_data]
            for item in config_data:
                apply_configuration(item)
