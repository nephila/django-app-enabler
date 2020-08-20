##########################
App Enabler
##########################


|Gitter| |PyPiVersion| |PyVersion| |GAStatus| |TestCoverage| |CodeClimate| |License|


============
Description
============

PoC autoconfigurator for django applications

``django-app-enabler`` goal is to reduce the configuration of a django application withing a django project a
one command operation to ease using django applications, both for newcomers and expert developers.

As configuring a django application can be both boring (as 90% are the usual steps editing ``settings.py`` and ``urls.py``)
and complex (as it's easy to overlook one vital configuration parameter), replacing this with a single command sounds like
a real benefit.

Key points
----------

* zero-knowledge tool to enable and configure django applications in a django project
* ``django-app-enabler`` will never be a package manager / replacement for pip/poetry/pipenv
* rely on specification file shipped by the target application to patch django project configuration

Caveats
-------

* Project is currenly just a proof of concept
* No stable release of any django application supporting this exists, currenty only `feature/installer-addon`_  branch of djangocms-blog support this autoconfiguration system
* No formal specification or documentation exist for addon confguration file
* Django project must have a single ``settings.py`` file and a single ``urls.py`` files. Currently no other layout is supported, this limitation will be removed very soon, though


============
Installation
============

``pip install https://github.com/nephila/django-app-enabler/archive/master.zip``

==============
Documentation
==============

Allow application supporting addon configurations to be configured automatically in the current django project.

General concept is that once a django package is installed, this application can be run from the project root and
the project is automatically updated with the minimal configuration required by the application to run.

Applied configurations are declared by the target application in a ``addon.json`` file included in the python package.

Sample file::

    {
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
            "sortedm2m"
        ],
        "settings": {
            "META_SITE_PROTOCOL": "http",
            "META_USE_SITES": true
        },
        "urls": [
            "djangocms_blog.taggit_urls"
        ]
    }

Sample execution flow
---------------------

::

    pip install djangocms-blog
    python -mapp_enabler djangocms_blog
    python manage.py migrate

After this the django application is configured and functional.

Additional configuration steps might be required according to the application
features and support level and must be documented by the application itself.



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


.. _feature/installer-addon: https://github.com/nephila/djangocms-blog/tree/feature/installer-addon
