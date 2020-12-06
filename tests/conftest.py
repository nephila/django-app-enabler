import os
import shutil
from pathlib import Path
from typing import Any, Dict

import pytest

from app_enabler.install import install
from app_enabler.patcher import setup_django
from tests.utils import get_project_dir, unload_django, working_directory

pytest_plugins = "pytester"


@pytest.fixture
def blog_package():
    """Ensure djangocms-blog is installed."""
    install("djangocms-blog")


@pytest.fixture
def django_setup(project_dir: str):
    """Setup django environment."""
    with working_directory(project_dir):
        os.environ["DJANGO_SETTINGS_MODULE"] = "test_project.settings"
        setup_django()
        yield
        unload_django()


@pytest.fixture
def teardown_django():
    """
    Reset django imports and configuration, undoing django.setup call.

    Use this fixture whenever django.setup is called during test execution (either explicitly or implicitly).

    Already called by :py:func:`django_setup`.
    """
    yield
    unload_django()


@pytest.fixture
def project_dir(pytester) -> Path:
    """Create a temporary django project structure."""
    original_project = get_project_dir()
    tmp_project = pytester.path / "tmp_project"
    shutil.rmtree(tmp_project, ignore_errors=True)
    shutil.copytree(original_project, tmp_project)
    yield tmp_project
    shutil.rmtree(tmp_project, ignore_errors=True)


@pytest.fixture
def addon_config() -> Dict[str, Any]:
    """Sample addon config."""
    return {
        "package-name": "djangocms-blog",
        "installed-apps": [
            "filer",
            "easy_thumbnails",
            "aldryn_apphooks_config",
            "parler",
            "taggit",
            "taggit_autosuggest",
            "meta",
            "djangocms_blog",
            "sortedm2m",
        ],
        "settings": {
            "META_SITE_PROTOCOL": "https",
            "META_USE_SITES": True,
            "MIDDLEWARE": ["django.middleware.gzip.GZipMiddleware"],
        },
        "urls": [["", "djangocms_blog.taggit_urls"]],
        "message": "Please check documentation to complete the setup",
    }
