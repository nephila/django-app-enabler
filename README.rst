##########################
App Enabler
##########################


|Gitter| |PyPiVersion| |PyVersion| |GAStatus| |TestCoverage| |CodeClimate| |License|


************
Description
************

PoC autoconfigurator for django applications

``django-app-enabler`` goal is to reduce the configuration of a django application to a
one command operation to ease using django applications, both for newcomers and expert developers.

As configuring a django application can be both boring (as 90% are the usual steps editing ``settings.py`` and ``urls.py``)
and complex (as it's easy to overlook one vital configuration parameter), replacing this with a single command sounds like
a real benefit.

Key points
==================

* zero-knowledge tool to enable and configure django applications in a django project
* rely on specification file shipped by the target application to patch django project configuration
* not a replacement for existing package or dependencies managers (pip / poetry / pipenv / ...)

Caveats
==================

* Project is currently just a proof of concept
* No formal specification or documentation exist (yet) for addon configuration file
* A lot of restrictions regarding the ``settings.py`` and ``urls.py`` files are currently in place
* Not all standard django settings options are currently supported

See `usage`_ for more details.

Compatible packages
===================

`Up-to-date list of compatible packages`_

.. |Gitter| image:: https://img.shields.io/badge/GITTER-join%20chat-brightgreen.svg?style=flat-square
    :target: https://gitter.im/nephila/applications
    :alt: Join the Gitter chat

.. |PyPiVersion| image:: https://img.shields.io/pypi/v/django-app-enabler.svg?style=flat-square
    :target: https://pypi.python.org/pypi/django-app-enabler
    :alt: Latest PyPI version

.. |PyVersion| image:: https://img.shields.io/pypi/pyversions/django-app-enabler.svg?style=flat-square
    :target: https://pypi.python.org/pypi/django-app-enabler
    :alt: Python versions

.. |GAStatus| image:: https://github.com/nephila/django-app-enabler/workflows/Tox%20tests/badge.svg
    :target: https://github.com/nephila/django-app-enabler
    :alt: Latest CI build status

.. |TestCoverage| image:: https://img.shields.io/coveralls/nephila/django-app-enabler/master.svg?style=flat-square
    :target: https://coveralls.io/r/nephila/django-app-enabler?branch=master
    :alt: Test coverage

.. |License| image:: https://img.shields.io/github/license/nephila/django-app-enabler.svg?style=flat-square
   :target: https://pypi.python.org/pypi/django-app-enabler/
    :alt: License

.. |CodeClimate| image:: https://codeclimate.com/github/nephila/django-app-enabler/badges/gpa.svg?style=flat-square
   :target: https://codeclimate.com/github/nephila/django-app-enabler
   :alt: Code Climate


.. _usage: https://django-app-enabler.readthedocs.io/en/latest/usage.html
.. _Up-to-date list of compatible packages: https://pypi.org/search/?q="django-app-enabler+addon"
