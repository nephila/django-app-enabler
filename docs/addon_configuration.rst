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

.. _extra_json:

****************************************
Extra configuration files specifications
****************************************

Extra configuration files (applied via :ref:`apply_cmd`) must conform to the same specifications below with two exceptions:

- all attributes are optional (i.e.: they can be completely omitted)
- the json file can contain a single object like for the ``addon.json`` case, or a list of objects conforming to the specifications.


Attributes
===========

The following attributes are currently supported:

* ``package-name`` [**required**]: package name as available on PyPi;
* ``installed-apps`` [**required**]: list of django applications to be appended in the project ``INSTALLED_APPS``
  setting. Application must be already installed when the configuration is processed, thus they must declared as
  package dependencies (or dependencies of direct dependencies, even if this is a bit risky);
* ``urls`` [optional]: list of urlconfs to be added to the project ``ROOT_URLCONF``. List can be empty if no url
  configuration is needed or it can be omitted.

  Each entry in the list must be in the ``[<patten>,<include-dotted-path>]`` format:

  * ``<pattern>`` must be a :py:func:`Django path() <django:django.urls.path>` pattern string, it can be empty
    (to add the urlconf to the root)
  * ``<include-dotted-path>`` must be a valid input for :py:func:`Django include() function <django:django.urls.include>`;
* ``settings`` [optional]: A dictionary of custom settings that will be added to project settings verbatim;
* ``message`` [optional]: A text message output after successful completion of the configuration;

Attribute format
----------------

``installed-apps`` and ``settings`` values can have the following formats:

- literal (``string``, ``int``, ``boolean``): value is applied as is
- ``dict`` with the following structure:

  - ``value: Any`` (required), the setting value
  - ``position: int``, if set and the target setting is a list, ``value`` is inserted at position
  - ``next: str``, name of an existing item before which the ``value`` is going to be inserted
  - ``key: str``, in case ``value`` is a dictionary, the dictionary key to be used to match existing settings value for duplicates and to match the ``next`` value


Merge strategy
==============

``settings`` items not existing in the target project settings are applied without further changes, so you can use whatever structure is needed.

``settings`` which already exists in the project and ``installed-apps`` configuration are merged with the ones already existing according to this strategy:

- setting does not exist -> custom setting is added verbatim
- setting exists and its value is a literal -> target project setting is overridden
- setting exists and its value is a list -> custom setting is merged:

  - if the custom setting is a literal -> its value is appended to the setting list
  - if it's a dictionary (see format above) ->

    - if ``next`` is defined, a value matching the ``next`` value is searched in the project setting and the custom setting ``value`` is inserted before the ``next`` element or at the top of the list if the value is not found; in case ``value`` (and items in the project settings) are dictionaries (like for example ``AUTH_PASSWORD_VALIDATORS``), a ``key`` attribute must be provided as a lookup key;
    - if ``position`` is defined, the custom setting value is inserted at that position;

In any case, if a value is already present, is not duplicated and is simply ignored.

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
            "META_USE_SITES": true,
            "MIDDLEWARE": [
                "django.middleware.gzip.GZipMiddleware",
                {"value": "django.middleware.http.ConditionalGetMiddleware", "position": 2},
                {
                    "value": "django.middleware.locale.LocaleMiddleware",
                    "next": "django.middleware.common.CommonMiddleware",
                },
            ],
            "AUTH_PASSWORD_VALIDATORS": [
                {
                    "value": {
                        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
                    },
                    "next": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
                    "key": "NAME",
                },
            ],
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
