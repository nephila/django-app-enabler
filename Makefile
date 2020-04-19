.PHONY: clean-pyc clean-build docs
PYTHON = python
TWINE_REPOSITORY_URL = https://devpi.iast.it/nephila/dev/

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "testall - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "release - package and upload a release"
	@echo "sdist - package"

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

lint:
	flake8 app_enabler
	django-app-helper app_enabler pyflakes

test:
	django-app-helper app_enabler test

test-all:
	tox

coverage:
	coverage erase
	coverage run `which django-app-helper` app_enabler test
	coverage report -m

sdist: clean
	python setup.py sdist
	ls -l dist

release: clean
	$(PYTHON) setup.py clean --all sdist bdist_wheel
	$(PYTHON) -mtwine upload --repository-url=$(TWINE_REPOSITORY_URL) dist/*

livehtml:
	sphinx-autobuild -b html -p5000 -H0.0.0.0 -E -j auto  -d docs/_build/doctrees --poll docs docs/_build/html
