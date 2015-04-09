# Pybedquilt makefile


all: build docs test


build:
	python setup.py bdist_wheel


install:
	python setup.py install


develop:
	python setup.py develop


test:
	python -m unittest discover tests


docs:
	python bin/generate_docs.py && mkdocs build


upload: build
	twine upload dist/*


.PHONY: build docs test upload
