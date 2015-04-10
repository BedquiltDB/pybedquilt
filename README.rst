PyBedquilt
==========

A Python driver for BedquiltDB.


Documentation
=============

https://pybedquilt.readthedocs.org/en/latest


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
