# Pybedquilt makefile


PYTHON=python2


all: build docs test


build:
	$(PYTHON) setup.py bdist_wheel


install:
	$(PYTHON) setup.py install


develop:
	$(PYTHON) setup.py develop


test: develop
	$(PYTHON) -m unittest discover tests


docs:
	$(PYTHON) bin/generate_docs.py && mkdocs build --clean


upload: build
	twine upload $$(ls -r1 dist/* | head -1)


.PHONY: build docs test upload
