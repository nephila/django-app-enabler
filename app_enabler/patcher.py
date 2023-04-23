import ast
import os  # noqa - used when eval'ing the management command
import sys
from types import CodeType
from typing import Any, Dict, Iterable, List, Optional, Union

import astor

from .errors import messages


def setup_django():
    """
    Initialize the django environment by leveraging ``manage.py``.

    This works by using ``manage.py`` to set the ``DJANGO_SETTINGS_MODULE`` environment variable for
    :py:func:`django.setup() <django:django.setup>` to work as it's unknown at runtime.

    This should be safer than reading the ``manage.py`` looking for the written variable as it rely on
    Django runtime behavior.

    Manage.py is monkeypatched in memory to remove the call "execute_from_command_line" and executed from memory.
    """
    import django

    try:
        managed_command = monkeypatch_manage("manage.py")
        eval(managed_command)
        django.setup()
    except FileNotFoundError:
        sys.stderr.write(messages["no_managepy"])
        sys.exit(1)


def monkeypatch_manage(manage_file: str) -> CodeType:
    """
    Patch ``manage.py`` to be executable without actually running any command.

    By using ast we remove the ``execute_from_command_line`` call and add an unconditional call to the main function.

    :param str manage_file: path to manage.py file
    :return: patched manage.py code
    """
    parsed = astor.parse_file(manage_file)
    # first patch run replace __name__ != '__main__' with a function call
    modified = DisableExecute().visit(parsed)
    # patching the module with the call to the main function as the standard one is not executed because
    # __name__ != '__main__'
    modified.body.append(ast.Expr(value=ast.Call(func=ast.Name(id="main", ctx=ast.Load()), args=[], keywords=[])))
    fixed = ast.fix_missing_locations(modified)
    return compile(fixed, "<string>", mode="exec")


class DisableExecute(ast.NodeTransformer):
    """
    Patch the ``manage.py`` module to remove the execute_from_command_line execution.
    """

    def visit_Expr(self, node: ast.AST) -> Any:  # noqa
        """Visit the ``Expr`` node and remove it if it matches ``'execute_from_command_line'``."""
        if (
            isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)  # noqa
            and node.value.func.id == "execute_from_command_line"  # noqa
        ):
            return None
        else:
            return node


def _ast_get_constant_value(ast_obj: Union[ast.Constant, ast.Str, ast.Num]) -> Any:
    """
    Extract the value from an ast.Constant / ast.Str / ast.Num obj.

    Required as in python 3.6 / 3.7 ast.Str / ast.Num are not subclasses of ast.Constant
    """
    try:
        return ast_obj.value
    except AttributeError:
        return ast_obj.s


def _ast_dict_key_index(dict_object: ast.Dict, lookup_key: str) -> Optional[int]:
    """Get the index of the lookup key in the ast Dict object."""
    try:
        return [_ast_get_constant_value(dict_key) for dict_key in dict_object.keys].index(lookup_key)
    except ValueError:
        return None


def _ast_dict_lookup(dict_object: ast.Dict, lookup_key: str) -> Optional[Any]:
    """Get the value of the lookup key in the ast Dict object."""
    key_position = _ast_dict_key_index(dict_object, lookup_key)
    if key_position is None:
        return None
    return _ast_get_constant_value(dict_object.values[key_position])


def _ast_get_object_from_value(val: Any) -> ast.Constant:
    """Convert value to AST via :py:func:`ast.parse`."""
    return ast.parse(repr(val)).body[0].value


def _update_list_setting(original_setting: List, configuration: Iterable):
    for config_value in configuration:
        # configuration items can be either strings (which are appended) or dictionaries which contains information
        # about the position of the item
        if isinstance(config_value, dict):
            value = config_value.get("value", None)
            position = config_value.get("position", None)
            relative_item = config_value.get("next", None)
            key = config_value.get("key", None)
            if relative_item:
                # if the item is already existing, we skip its insertion
                position = None
                if key:
                    # if the match is against a key we must both flatted the original setting to a list of literals
                    # extracting the key value and getting the key value for the setting we want to add
                    flattened_data = [_ast_dict_lookup(item, key) for item in original_setting]
                    check_value = value.get(key, None)
                else:
                    flattened_data = [_ast_get_constant_value(item) for item in original_setting]
                    check_value = value
                if any(flattened_data) and check_value not in flattened_data:
                    try:
                        position = flattened_data.index(relative_item)
                    except ValueError:
                        # in case the relative item is not found we add the value on top
                        position = 0
            if position is not None:
                original_setting.insert(position, _ast_get_object_from_value(value))
        else:
            if config_value not in [_ast_get_constant_value(item) for item in original_setting]:
                original_setting.append(_ast_get_object_from_value(config_value))


def update_setting(project_setting: str, config: Dict[str, Any]):
    """
    Patch the settings module to include addon settings.

    Original file is overwritten. As file is patched using AST, original comments and file structure is lost.

    :param str project_setting: project settings file path
    :param dict config: addon setting parameters
    """
    parsed = astor.parse_file(project_setting)
    existing_setting = []
    addon_settings = config.get("settings", {})
    addon_installed_apps = config.get("installed-apps", [])
    constant_subclasses = (ast.Constant, ast.Num, ast.Str, ast.Bytes, ast.NameConstant, ast.Ellipsis)

    for node in parsed.body:
        if isinstance(node, ast.Assign) and node.targets[0].id == "INSTALLED_APPS":
            _update_list_setting(node.value.elts, addon_installed_apps)
        elif isinstance(node, ast.Assign) and node.targets[0].id in addon_settings.keys():  # noqa
            config_param = addon_settings[node.targets[0].id]
            if isinstance(node.value, ast.List) and (
                isinstance(config_param, list) or isinstance(config_param, tuple)
            ):
                _update_list_setting(node.value.elts, config_param)
            elif isinstance(node.value, ast.Dict):
                for dict_key, dict_value in config_param.items():
                    ast_position = _ast_dict_key_index(node.value, dict_key)
                    if ast_position is None:
                        node.value.keys.append(_ast_get_object_from_value(dict_key))
                        node.value.values.append(_ast_get_object_from_value(dict_value))
                    else:
                        node.value.values[ast_position] = _ast_get_object_from_value(dict_value)
                pass
            elif type(node.value) in constant_subclasses:
                # check required as in python 3.6 / 3.7 ast.Str / ast.Num are not subclasses of ast.Constant
                node.value = _ast_get_object_from_value(config_param)
            existing_setting.append(node.targets[0].id)
    for name, value in addon_settings.items():
        if name not in existing_setting:
            parsed.body.append(ast.Assign(targets=[ast.Name(id=name)], value=_ast_get_object_from_value(value)))

    src = astor.to_source(parsed)

    with open(project_setting, "w") as fp:
        fp.write(src)


def update_urlconf(project_urls: str, config: Dict[str, Any]):
    """
    Patch the ``ROOT_URLCONF`` module to include addon url patterns.

    Original file is overwritten. As file is patched using AST, original comments and file structure is lost.

    :param str project_urls: project urls.py file path
    :param dict config: addon urlconf configuration
    """
    parsed = astor.parse_file(project_urls)

    addon_urls = config.get("urls", [])
    for node in parsed.body:
        if isinstance(node, ast.ImportFrom) and node.module == "django.urls":
            existing_names = [alias.name for alias in node.names]
            if "include" not in existing_names:
                node.names.append(ast.alias(name="include", asname=None))
        elif isinstance(node, ast.Assign) and node.targets[0].id == "urlpatterns":
            existing_urlconf = []
            for url_line in node.value.elts:
                # the following list comprehension matches path() / url() instances in urlpatterns
                # using the `include()` statement as argument. ie.
                # - matched: path('', include('cms.urls')
                # - not matched: path('sitemap.xml', sitemap, {})
                # we look for ast.Call (outer loop) wrapping ast.Str (inner loop),
                # and we assume all is wrapped in ast.Call (as we cycle on url_line.args)
                urlconf_path = [
                    subarg.s
                    for stmt in url_line.args
                    if isinstance(stmt, ast.Call)
                    for subarg in stmt.args
                    if isinstance(subarg, ast.Str)
                ]
                if urlconf_path:
                    existing_urlconf.extend(urlconf_path)
            for pattern, urlconf in addon_urls:
                if urlconf not in existing_urlconf:
                    part = ast.parse(f"path('{pattern}', include('{urlconf}'))")
                    node.value.elts.append(part.body[0].value)

    src = astor.to_source(parsed)

    with open(project_urls, "w") as fp:
        fp.write(src)
