import psycopg2
import os
import getpass
import unittest
import json
import pybedquilt
import inspect


# CREATE DATABASE bedquilt_test
#   WITH OWNER = {{owner}}
#        ENCODING = 'UTF8'
#        TABLESPACE = pg_default
#        LC_COLLATE = 'en_GB.UTF-8'
#        LC_CTYPE = 'en_GB.UTF-8'
#        CONNECTION LIMIT = -1;


def get_pg_connection():
    """
    Get a connection to localhost/bedquilt_test,
    as the current user.
    """
    return psycopg2.connect(
        database='bedquilt_test',
        user=getpass.getuser()
    )
PG_CONN  = get_pg_connection()


def clean_database(conn):
    cur = conn.cursor()
    cur.execute("select bq_list_collections();")
    result = cur.fetchall()
    if result is not None:
        for collection in result:
            cur.execute(
                "select bq_delete_collection('{}')".format(collection[0]))

    conn.commit()

class BedquiltTestCase(unittest.TestCase):

    def setUp(self):
        self.conn = PG_CONN
        self.cur = self.conn.cursor()
        clean_database(self.conn)

        self.database_name = 'bedquilt_test'

    def tearDown(self):
        self.conn.rollback()

    def _get_test_client(self):
        return pybedquilt.BedquiltClient(
            'dbname={}'.format(self.database_name))

    def _test_save(self, coll, doc, expected_result):

        if (inspect.isclass(expected_result)
            and issubclass(expected_result, Exception)):
            with self.assertRaises(expected_result):
                coll.save(doc)
            self.conn.rollback()

        else:
            result = coll.save(doc)
            self.assertEqual(result, expected_result)
