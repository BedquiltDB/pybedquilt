# Pybedquilt makefile


all: build docs test


build:
	python setup.py bdist_wheel


install:
	python setup.py install


develop:
	python setup.py develop


test: develop
	python -m unittest discover tests


docs:
	python bin/generate_docs.py && mkdocs build --clean


upload: build
	twine upload $$(ls -r1 dist/* | head -1)


.PHONY: build docs test upload
