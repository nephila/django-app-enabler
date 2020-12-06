.. _usage:

#####
Usage
#####

``django-app-enabler`` allow application supporting :ref:`addon_configuration` to be installed and configured automatically in the current django project.

.. _installation:

*************************
Installation
*************************

``pip install django-app-enabler``

*************************
Commands
*************************

* :ref:`enable \<module_name\> <enable_cmd>`: Configure an application
* :ref:`install \<package-name\> <install_cmd>`: Install and configure an application


**********************
Sample execution flow
**********************

.. code-block:: bash

    python -mapp_enabler install djangocms-blog~=1.2.1
    python manage.py migrate

After this the django application is configured and functional.

Additional configuration steps might be required according to the application
features and support level and must be documented by the application itself.


.. _enable_cmd:

*************************
Application configuration
*************************

The core of ``django-app-enabler`` is its Django configuration patching engine.

The general concept is that once a django package is installed, ``app-enabler`` can be run from the project root and
the project is automatically updated with the minimal configuration required by the application to run (or any superset
of this definition).

Applied configurations are declared by the target application in a :ref:`addon_json` file included in the python package.

Example:

.. code-block:: bash

    python -mapp_enabler enabler djangocms_blog


See :ref:`limitations` for limitations and caveats.

.. _install_cmd:

*************************
Application Installation
*************************

As a convenience ``django-app-enabler`` can execute ``pip install`` on your behalf, though step this is not required.

The ``install`` command will both install the package and enable it.

Installation is executed via the ``install`` command which a

.. code-block:: bash

    python -mapp_enabler install djangocms-blog~=1.2.0

.. note:: ``django-app-enabler`` is not intended as a replacement (or sidekick) of existing package / dependencies manager.
          The installation step is only intended as a convenience command for those not sticking to any specific workflow.
          If you are using anything than manual ``pip`` to install packages, please stick to it and just use :ref:`enable_cmd`.
