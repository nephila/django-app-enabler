import json
from importlib import import_module
from typing import Optional

from pkg_resources import resource_stream


def load_addon(module_name: str) -> Optional[dict]:
    """
    Load addon configuration from json file stored in package resources.

    If addon has no configuration, return ``None``.

    :param module_name: name of the python module to load as application
    :type module_name: str
    :return: addon configuration
    :rtype: Optional[dict]
    """
    try:
        fp = resource_stream(module_name, "addon.json")
        return json.load(fp)
    except Exception:
        pass


def get_settings_path(setting: str) -> str:
    """Fetch the path of the settings module."""
    settings_module = import_module(setting.SETTINGS_MODULE)
    return settings_module.__file__


def get_urlconf_path(setting: str) -> str:
    """Fetch the path of the urls module."""
    urlconf_module = import_module(setting.ROOT_URLCONF)
    return urlconf_module.__file__
