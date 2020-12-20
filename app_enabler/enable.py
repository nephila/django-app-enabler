import sys
from importlib import import_module
from types import ModuleType
from typing import Any, Dict

import django.conf

from .django import get_settings_path, get_urlconf_path, load_addon
from .patcher import setup_django, update_setting, update_urlconf


def _verify_settings(imported: ModuleType, application_config: Dict[str, Any]) -> bool:
    """
    Check that addon config has been properly set in patched settings.

    :param ModuleType imported:  Update settings module
    :param dict application_config: addon configuration
    """
    test_passed = True
    for app in application_config["installed-apps"]:
        test_passed = test_passed and app in imported.INSTALLED_APPS
    for key, value in application_config["settings"].items():
        if isinstance(value, list):
            for item in value:
                test_passed = test_passed and item in getattr(imported, key)
        else:
            test_passed = test_passed and getattr(imported, key) == value
    return test_passed


def _verify_urlconf(imported: ModuleType, application_config: Dict[str, Any]) -> bool:
    """
    Check that addon urlconf has been properly added in patched urlconf.


    :param ModuleType imported: Update ``ROOT_URLCONF`` module
    :param dict application_config: addon configuration
    """
    # include function is added by our patcher, soo we must ensure it is available
    test_passed = bool(imported.include)
    included_urls = [url[1] for url in application_config["urls"]]
    # as we want to make sure urlpatterns is really tested, we check both that an existing module of the correct type
    # is the module from addon config, and that the assert is reached for real
    urlpatterns_checked = False
    for urlpattern in imported.urlpatterns:
        if isinstance(urlpattern.urlconf_name, ModuleType):
            urlpatterns_checked = True
            test_passed = test_passed and urlpattern.urlconf_name.__name__ in included_urls
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
    sys.stdout.write(message)


def enable(application: str, verbose: bool = False):
    """
    Enable django application in the current project

    :param str application: python module name to enable. It must be the name of a Django application.
    :param bool verbose: Verbose output (currently unused)
    """

    setup_django()

    setting_file = get_settings_path(django.conf.settings)
    urlconf_file = get_urlconf_path(django.conf.settings)
    application_config = load_addon(application)
    if application_config:
        update_setting(setting_file, application_config)
        update_urlconf(urlconf_file, application_config)
        if verify_installation(django.conf.settings, application_config):
            output_message(application_config["message"])
