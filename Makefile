# Pybedquilt makefile


all: build docs test


build:
	python setup.py build


install:
	python setup.py install


develop:
	python setup.py develop


test:
	python -m unittest discover tests


docs:
	python bin/generate_docs.py && mkdocs build


upload:
	python setup.py upload


.PHONY: build docs test upload
