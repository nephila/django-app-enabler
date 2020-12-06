#!/usr/bin/env python

from tempfile import mkdtemp

HELPER_SETTINGS = dict(
    INSTALLED_APPS=["app_enabler"],
    FILE_UPLOAD_TEMP_DIR=mkdtemp(),
)


def run():
    from app_helper import runner

    runner.run("app_enabler")


def setup():
    import sys

    from app_helper import runner

    runner.setup("app_enabler", sys.modules[__name__])


if __name__ == "__main__":
    run()

if __name__ == "helper":
    # this is needed to run cms_helper in pycharm
    setup()
