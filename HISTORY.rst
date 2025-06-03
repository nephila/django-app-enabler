.. :changelog:

*******
History
*******

.. towncrier release notes start

0.5.0 (2025-06-03)
==================

Bugfixes
--------

- Pin click version to < 8.2.0 (#84)


0.4.0 (2025-01-17)
==================

Bugfixes
--------

- Fix docs build, drop support for Django < 4.2 and python < 3.10 (#64)


0.3.0 (2023-11-09)
==================

Features
--------

- Improve merge strategy to support all the basic standard Django settings (#5)
- Add support for external configuration json (#9)
- Upgrade to Django 3.2/4.2 (#32)
- Switch to Coveralls Github action (#56)
- Migrate to bump-my-version (#58)


0.2.0 (2020-12-27)
==================

Features
--------

- Add CLI utility (#20)


Bugfixes
--------

- Close resource_stream file pointer (#19)
- Fix importing include multiple times in urlconf (#21)
- Add test to verify no multiple urlconf are added (#25)


0.1.1 (2020-12-21)
==================

Features
--------

- Add codeql action (#15)


Bugfixes
--------

- Fix errors with urlconf patching (#17)


0.1.0 (2020-12-20)
==================

Initial release

Features
--------

- Add install command (#1)
- Add tests (#2)
- Add support for message addon config parameter (#11)


Improved Documentation
----------------------

- Improve documentation (#1)
