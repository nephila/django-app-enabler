import json
from importlib import import_module
from typing import Any, Dict, Optional

import django.conf
from pkg_resources import resource_stream


def load_addon(module_name: str) -> Optional[Dict[str, Any]]:
    """
    Load addon configuration from json file stored in package resources.

    If addon has no configuration, return ``None``.

    :param str module_name: name of the python module to load as application
    :return: addon configuration
    """
    try:
        with resource_stream(module_name, "addon.json") as fp:
            data = json.load(fp)
        return data
    except Exception:
        pass


def get_settings_path(setting: "django.conf.LazySettings") -> str:
    """
    Get the path of the django settings file path from the django settings object.

    :param django.conf.LazySettings setting: Django settings object
    :return: path to the settings file
    """
    settings_module = import_module(setting.SETTINGS_MODULE)
    return settings_module.__file__


def get_urlconf_path(setting: "django.conf.LazySettings") -> str:
    """
    Get the path of the django urlconf file path from the django settings object.

    :param django.conf.LazySettings setting: Django settings object
    :return: path to the settings file
    """
    urlconf_module = import_module(setting.ROOT_URLCONF)
    return urlconf_module.__file__
