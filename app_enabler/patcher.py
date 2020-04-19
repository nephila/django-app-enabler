import ast
import sys
from types import CodeType

import astor
import django


def setup_django():
    """
    Initialize the django environment by leveraging manage.py.

    This works by using manage.py to set the DJANGO_SETTINGS_MODULE environment variable for django.setup to work.

    Manage.py is monkeypatched in memory to remove the call "execute_from_command_line" and executed from memory.
    """
    try:
        managed_command = monkeypatch_manage("manage.py")
        eval(managed_command)
        django.setup()
    except FileNotFoundError:
        print(
            "app-enabler must be execute in the same directory as the project manage.py file"
        )
        sys.exit(1)


def monkeypatch_manage(manage_file: str) -> CodeType:
    """
    Patch manage.py to be executable without actually running any command.

    By using ast we remove the "execute_from_command_line" call and add an unconditional call to the main function.
    """
    parsed = astor.parse_file(manage_file)
    modified = DisableExecute().visit(parsed)
    # patching the module with the call to the main function as the standard one is not executed because
    # __name__ != '__main__'
    modified.body.append(
        ast.Expr(
            value=ast.Call(
                func=ast.Name(id="main", ctx=ast.Load()), args=[], keywords=[]
            )
        )
    )
    fixed = ast.fix_missing_locations(modified)
    return compile(fixed, "<string>", mode="exec")


class DisableExecute(ast.NodeTransformer):
    """
    Patch the managepy module to remove the execute_from_command_line execution.
    """

    def visit_Expr(self, node: ast.AST) -> Any:  # noqa
        """Visit the Expr node and remove it if it matches execute_from_command_line."""
        # long chained checks, but wehave to remove the entire call, thus w have to remove the Expr node
        if (
            isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)  # noqa
            and node.value.func.id == "execute_from_command_line"  # noqa
        ):
            return None
        else:
            return node


def update_setting(project_setting, config):
    """
    Patch the settings module to include addon settings.

    Original file is overwritten. As file is patched using AST, original comments and file structure is lost.

    :param project_setting: project urls.py file path
    :type projectproject_setting_urls: str
    :param config: addon setting parameters
    :type config: str
    """
    parsed = astor.parse_file(project_setting)
    existing_setting = []
    for node in parsed.body:
        if isinstance(node, ast.Assign) and node.targets[0].id == "INSTALLED_APPS":
            installed_apps = [name.s for name in node.value.elts]
            addon_apps = [
                ast.Constant(app)
                for app in config["installed-apps"]
                if app not in installed_apps
            ]
            node.value.elts.extend(addon_apps)
        elif (
            isinstance(node, ast.Assign)
            and node.targets[0].id in config["settings"].keys()  # noqa
        ):
            existing_setting.append(node.targets[0].id)
    for name, value in config["settings"].items():
        if name not in existing_setting:
            parsed.body.append(
                ast.Assign(targets=[ast.Name(id=name)], value=ast.Constant(value))
            )

    src = astor.to_source(parsed)

    with open(project_setting, "w") as settings:
        settings.write(src)


def update_urlconf(project_urls: str, config: dict):
    """
    Patch the ROOT_URLCONF module to include addon url patterns.

    Original file is overwritten. As file is patched using AST, original comments and file structure is lost.

    :param project_urls: project urls.py file path
    :type project_urls: str
    :param config: addon urlconf configuration
    :type config: str
    """
    parsed = astor.parse_file(project_urls)

    for node in parsed.body:
        if isinstance(node, ast.Assign) and node.targets[0].id == "urlpatterns":
            existing_url = []
            for url_line in node.value.elts:
                calls = [
                    subarg.s
                    for stmt in url_line.args
                    if isinstance(stmt, ast.Call)
                    for subarg in stmt.args
                    if isinstance(subarg, ast.Str)
                ]
                if calls:
                    existing_url.extend(calls)
            for url in config["urls"]:
                if url not in existing_url:
                    part = ast.parse("url(r'^', include('%s'))" % url)
                    node.value.elts.append(part.body[0].value)

    src = astor.to_source(parsed)

    with open(project_urls, "w") as settings:
        settings.write(src)
