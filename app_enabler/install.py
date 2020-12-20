import logging
import subprocess
import sys
from typing import Optional

import pkg_resources
from pkg_resources import Requirement

logger = logging.getLogger("")


def install(package: str, verbose: bool = False, pip_options: str = ""):
    """
    Install the package.

    Installation is done via pip executed as a subprocess to ensure maximum compatibility.

    :param str package: Package name
    :param bool verbose: Verbose output
    :param str pip_options: Additional options passed to pip
    """
    args = ["install", "--disable-pip-version-check"]
    if not verbose:
        args.append("-q")
    if pip_options:
        args.extend([opt for opt in pip_options.split(" ") if opt])
    args.append(package)
    cmd = [sys.executable, "-mpip"] + args
    if verbose:
        sys.stdout.write("python path: {}\n".format(sys.executable))
        sys.stdout.write("packages install command: {}\n".format(" ".join(cmd)))
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        sys.stdout.write(output.decode("utf-8"))
        return True
    except subprocess.CalledProcessError as e:  # pragma: no cover
        logger.error("cmd : {} :{}".format(e.cmd, e.output))
        raise


def get_application_from_package(package: str) -> Optional[str]:
    """
    Detect the first in alphabetical order module provided by a package.

    This approach is a bit simplistic, but as we only need this to get the ``addon.json`` file specified by this
    package, we can easily enforce this restriction.

    :param str package: package name (or rather its requirement string). It can be anything complying with PEP508
    :return: main (first) module name; if ``None``, package is not available in the current virtualenv
    """
    try:
        distribution = pkg_resources.get_distribution(Requirement.parse(package))
    except pkg_resources.DistributionNotFound:
        return
    try:
        return distribution.get_metadata("top_level.txt").split()[0]
    except (FileNotFoundError, IndexError):  # pragma: no cover
        return
