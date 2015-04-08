# Pybedquilt makefile


all: build doc test


build:
	python setup.py build


install:
	python setup.py install


develop:
	python setup.py develop


test:
	python -m unittest discover tests


doc:
	python bin/generate_docs.py && mkdocs build
