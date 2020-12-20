from app_enabler.django import get_settings_path, get_urlconf_path, load_addon
from tests.utils import working_directory


def test_load_addon(blog_package):
    """addon.json file is loaded from the package name."""
    addon_config = load_addon("djangocms_blog")
    assert addon_config["package-name"] == "djangocms-blog"
    assert addon_config["installed-apps"]


def test_load_addon_no_application(blog_package):
    """addon.json file is not loaded from a non existing package."""
    assert load_addon("djangocms_blog2") is None


def test_get_settings_path(django_setup, project_dir):
    """Settings file path can is retrieved from settings in memory module."""
    from django.conf import settings

    with working_directory(project_dir):
        expected = project_dir / "test_project" / "settings.py"
        settings_file = get_settings_path(settings)
        assert str(settings_file) == str(expected)


def test_get_urlconf_path(django_setup, project_dir):
    """Project urlconf file path is retrieved from settings in memory module."""
    from django.conf import settings

    with working_directory(project_dir):
        expected = project_dir / "test_project" / "urls.py"
        urlconf_file = get_urlconf_path(settings)
        assert str(urlconf_file) == str(expected)
