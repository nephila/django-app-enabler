import os
import sys
from pathlib import Path
from subprocess import CalledProcessError
from unittest.mock import call, patch

import pytest
from click.testing import CliRunner

from app_enabler.cli import cli
from app_enabler.errors import messages
from tests.utils import working_directory


def test_cli_install_wrong_dir(blog_package):
    """Running install command from the wrong directory raise an error."""
    with patch("app_enabler.cli.install_fun") as install_fun:
        runner = CliRunner()
        result = runner.invoke(cli, ["--verbose", "install", "djangocms-blog"])
        assert result.exit_code == 1
        assert result.output.strip() == messages["no_managepy"].strip()
        install_fun.assert_called_once()
        assert install_fun.call_args_list == [call("djangocms-blog", verbose=True, pip_options="")]


def test_cli_sys_path(project_dir, blog_package):
    """Running install command from the wrong directory raise an error."""
    with patch("app_enabler.cli.enable_fun"):
        # not using working_directory context manager to skip setting the sys.path (which is what we want to test)
        os.chdir(str(project_dir))
        runner = CliRunner()
        runner.invoke(cli, ["enable", "djangocms-blog"])
        assert str(project_dir) == sys.path[0]


def test_cli_install(project_dir, blog_package):
    """Running install command calls the business functions with the correct arguments."""
    with (
        patch("app_enabler.cli.enable_fun") as enable_fun,
        patch("app_enabler.cli.install_fun") as install_fun,
        working_directory(project_dir),
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["--verbose", "install", "djangocms-blog"])
        assert result.exit_code == 0
        install_fun.assert_called_once()
        assert install_fun.call_args_list == [call("djangocms-blog", verbose=True, pip_options="")]

        enable_fun.assert_called_once()
        assert enable_fun.call_args_list == [call("djangocms_blog", verbose=True)]


@pytest.mark.parametrize("verbose", (True, False))
def test_cli_install_error_verbose(verbose: bool):
    """Error raised during package install is reported to the user."""
    with patch("app_enabler.cli.enable_fun") as enable_fun, patch("app_enabler.cli.install_fun") as install_fun:
        install_fun.side_effect = CalledProcessError(cmd="cmd", returncode=1)

        runner = CliRunner()
        if verbose:
            args = ["--verbose"]
        else:
            args = []
        args.extend(("install", "djangocms-blog"))
        result = runner.invoke(cli, args)

        if verbose:
            assert result.exit_code == 1
            assert not result.output
            assert str(result.exception) == messages["install_error"].format(package="djangocms-blog")
            assert isinstance(result.exception, RuntimeError)
        else:
            assert result.exit_code == 0
            assert result.output == messages["install_error"].format(package="djangocms-blog")

        install_fun.assert_called_once()
        assert install_fun.call_args_list == [call("djangocms-blog", verbose=verbose, pip_options="")]

        enable_fun.assert_not_called()


@pytest.mark.parametrize("verbose", (True, False))
def test_cli_install_bad_application_verbose(verbose: bool):
    """Error due to bad application name is reported to the user."""
    with (
        patch("app_enabler.cli.enable_fun") as enable_fun,
        patch("app_enabler.cli.install_fun"),
        patch("app_enabler.cli.get_application_from_package") as get_application_from_package,
    ):
        get_application_from_package.return_value = None

        runner = CliRunner()
        if verbose:
            args = ["--verbose"]
        else:
            args = []
        args.extend(("install", "djangocms-blog"))
        result = runner.invoke(cli, args)

        if verbose:
            assert result.exit_code == 1
            assert not result.output
            assert str(result.exception) == messages["enable_error"].format(package="djangocms-blog")
            assert isinstance(result.exception, RuntimeError)
        else:
            assert result.exit_code == 0
            assert result.output == messages["enable_error"].format(package="djangocms-blog")

        enable_fun.assert_not_called()


@pytest.mark.parametrize("verbose", (True, False))
def test_cli_enable(verbose: bool):
    """Running enable command calls the business functions with the correct arguments."""
    with patch("app_enabler.cli.enable_fun") as enable_fun:
        runner = CliRunner()
        if verbose:
            args = ["--verbose"]
        else:
            args = []
        args.extend(("enable", "djangocms_blog"))
        result = runner.invoke(cli, args)
        assert result.exit_code == 0

        enable_fun.assert_called_once()
        assert enable_fun.call_args_list == [call("djangocms_blog", verbose=verbose)]


@pytest.mark.parametrize("verbose", (True, False))
def test_cli_apply(verbose: bool):
    """Running apply command calls the business functions with the correct arguments."""
    with patch("app_enabler.cli.apply_configuration_set") as apply_configuration_set:
        runner = CliRunner()
        if verbose:
            args = ["--verbose"]
        else:
            args = []

        configs = ("/path/config1.json", "/path/config2.json")
        args.extend(("apply", *configs))
        result = runner.invoke(cli, args)
        assert result.exit_code == 0

        apply_configuration_set.assert_called_once()
        assert apply_configuration_set.call_args_list == [call([Path(config) for config in configs], verbose=verbose)]


@pytest.mark.parametrize("verbose", (True, False))
def test_cli_function(verbose: bool):
    """Running cli without commands return info message."""
    with patch("app_enabler.cli.enable_fun") as enable_fun, patch("app_enabler.cli.install_fun") as install_fun:
        runner = CliRunner()
        if verbose:
            args = ["--verbose"]
        else:
            args = []
        result = runner.invoke(cli, args)
        install_fun.assert_not_called()
        enable_fun.assert_not_called()

        if verbose:
            assert result.exit_code == 2
            assert "Error: Missing command." in result.output
        else:
            assert result.exit_code == 0
            assert "Commands:" in result.output
