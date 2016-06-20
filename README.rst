PyBedquilt
==========

A Python driver for BedquiltDB_.

.. _BedquiltDB: http://bedquiltdb.github.io

Installation
============

To install pybedquilt from pip::
   $ pip install pybedquilt


Documentation
=============

https://pybedquilt.readthedocs.org/en/latest


Example App
===========

https://github.com/BedquiltDB/webapp-example


Tests
=====

First, ensure there is a postgresql database running with bedquiltdb installed
on a "bedquilt_test" database, then run::
   $ make test


Development prerequisites
=========================

- Python >= 2.7
- pyscopg2
- gnu make
- mkdocs (for building docs)
