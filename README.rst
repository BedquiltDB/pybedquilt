PyBedquilt
==========

A Python2/3 driver for BedquiltDB_.

.. _BedquiltDB: http://bedquiltdb.github.io


Documentation
=============

https://pybedquilt.readthedocs.org/en/latest


Example App
===========

https://github.com/BedquiltDB/webapp-example


Tests
=====

First, ensure there is a postgresql database running with bedquiltdb installed
on a "bedquilt_test" database, then once a suitable python environment is set up, run::
   $ make test


Development and Test prerequisites
=========================

- Python >= 2.7
- pyscopg2
- gnu make
- mkdocs (for building docs)
