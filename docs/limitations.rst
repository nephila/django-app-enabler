.. _limitations:


###############
Limitations
###############

Paching features have currently the following limitations:

*************************
settings.py
*************************

* Only single file ``settings.py`` are currently supported.
  In case you are using splitted settings, the only way to use ``django-app-enabler`` is to have at least an empty
  ``INSTALLED_APPS`` list in the settings file declared in ``DJANGO_SETTINGS_MODULE``.
* Only ``INSTALLED_APP`` setting is supported as a standard Django setting to be patched. Others like ``MIDDLEWARE``,
  ``TEMPLATES`` etc are not supported yet. Any custom setting is supported, though.
* While extra requirements will be installed when including them in the package argument (as in ``djangocms-blog[search]``),
  they will not be added to ``INSTALLED_APPS`` and they must be added manually after command execution.


*************************
urls.py
*************************

* Only single file ``urls.py`` are currently supported.
  In case you are using splitted settings, the only way to use ``django-app-enabler`` is to have at least an empty
  ``urlpatterns`` list in the ``settings.ROOT_URLCONF`` file.
