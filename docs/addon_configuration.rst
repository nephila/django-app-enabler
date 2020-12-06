.. _addon_configuration:

#################################
Addon configuration specification
#################################

``django-app-enabler`` support can be enabled by adding a :ref:`addon_json` to any django application
(see below for the structure).


.. note: To make easier to find compatible packages, add ``django-app-enabler`` to the package keywords.

See :ref:`limitations` for limitations and caveats.

.. _addon_json:

***********
addon.json
***********

``addon.json`` is the only configuration file needed to support ``django-app-enabler`` and it **must** provide at least
the minimal setup to make the application up an running on a clean django project.

.. warning:: The file must be included in root of the first (alphabetically) module of your application package.
             See :ref:`packaging` for details.

Attributes
===========

The following attributes are currently supported:

* ``package-name`` [**required**]: package name as available on PyPi;
* ``installed-apps`` [**required**]: list of django applications to be appended in the project ``INSTALLED_APPS``
  setting. Application must be already installed when the configuration is processed, thus they must declared as
  package dependencies (or depedencies of direct dependencies, even if this is a bit risky);
* ``urls`` [**required**]: list of urlconfs to be added to the project ``ROOT_URLCONF``. List can be empty if no url
  configuration is needed.

  Each entry in the list must be in the ``[<patten>,<include-dotted-path>]`` format:

  * ``<pattern>`` must be a :py:func:`Django path() <django:django.urls.path>` pattern string, it can be empty
    (to add the urlconf to the root)
  * ``<include-dotted-path>`` must be a valid input for :py:func:`Django include() function <django:django.urls.include>`;
* ``settings`` [optional]: A dictionary of custom settings that will be added to project settings verbatim;
* ``message`` [optional]: A text message output after succesfull completion of the configuration;


Sample file
===========

.. code-block:: json

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
            "META_SITE_PROTOCOL": "https",
            "META_USE_SITES": true
        },
        "urls": [
            ["", "djangocms_blog.taggit_urls"]
        ],
        "message": "Please check documentation to complete the setup"
    }


.. _packaging:

**********
Packaging
**********

TBA
