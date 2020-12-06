import sys
from subprocess import CalledProcessError
from unittest.mock import patch

import pytest

from app_enabler.install import get_application_from_package, install


def test_get_application_not_existing():
    """Retrieving the main module from a non existing package returns None."""
    assert get_application_from_package("bla_bla") is None


@pytest.mark.parametrize(
    "package,expected",
    (
        ("pytest", "_pytest"),
        ("django", "django"),
        ("six", "six"),
    ),
)
def test_get_application(package, expected):
    """First module of the given package is retrieved."""
    assert get_application_from_package(package) == expected


def test_install_real():
    """Package is installed via app_enabler.install.install function."""
    assert install("djangocms_blog")
    import djangocms_blog

    # quick and dirty way to test that package is available
    assert djangocms_blog


def test_install_args(capsys):
    """Package is installed via app_enabler.install.install function."""
    with patch("subprocess.check_output") as check_output:
        check_output.return_value = b"Installed"
        args = [sys.executable, "-mpip", "install", "--disable-pip-version-check", "-v", "djangocms_blog"]
        installed = install("djangocms_blog", pip_options="-v", verbose=True)

        captured = capsys.readouterr()
        assert installed
        assert check_output.call_args[0][0] == args
        assert f"python path: {sys.executable}" in captured.out
        assert f"packages install command: {sys.executable}" in captured.out


def test_install_error(capsys):
    """Package installation error report detailed message."""
    with patch("subprocess.check_output") as check_output:
        check_output.side_effect = CalledProcessError(cmd="cmd", returncode=1)

        with pytest.raises(CalledProcessError) as exception:
            installed = install("djangocms_blog")
            captured = capsys.readouterr()

            assert installed is None
            assert exception.cmd
            assert exception.return_code == 1
            assert exception.output

            assert f"python path: {sys.executable}" in captured.out
            assert f"packages install command: {sys.executable}" in captured.out
