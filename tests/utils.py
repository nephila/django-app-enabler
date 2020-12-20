import contextlib
import os
import sys
from pathlib import Path


@contextlib.contextmanager
def working_directory(path: Path):
    """Change working directory and returns to previous on exit."""
    prev_cwd = Path.cwd()
    os.chdir(str(path))
    sys.path.insert(0, str(path))
    try:
        yield
    finally:
        os.chdir(prev_cwd)
        sys.path.remove(str(path))


def get_project_dir() -> Path:
    """
    Sample project directory

    :return str: sample project directory
    """
    return Path(__file__).parent / "sample"


def unload_django():
    """Tear down django initialization by unloding modules and resetting apps state."""
    project_modules = [
        module_name
        for module_name in sys.modules.keys()
        if module_name.startswith("django") or module_name.startswith("test_project")
    ]
    for module in project_modules:
        if module in sys.modules:
            del sys.modules[module]

    from django.apps import apps

    apps.clear_cache()
    apps.ready = False
    apps.models_ready = False
    apps.apps_ready = False
    apps.loading = False
    apps.app_configs = {}
