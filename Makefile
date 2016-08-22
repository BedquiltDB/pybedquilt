# Pybedquilt makefile


all: build docs test


build:
	python2 setup.py bdist_wheel


install:
	python2 setup.py install


develop:
	python2 setup.py develop


test: develop
	python2 -m unittest discover tests


docs:
	python2 bin/generate_docs.py && mkdocs build --clean


upload: build
	twine upload $$(ls -r1 dist/* | head -1)


.PHONY: build docs test upload
