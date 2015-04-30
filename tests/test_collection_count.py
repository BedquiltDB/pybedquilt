import testutils
import json
import string
import psycopg2


class TestCollectionCount(testutils.BedquiltTestCase):

    def test_on_empty_collection(self):
        client = self._get_test_client()
        client.create_collection('things')

        coll = client.collection('things')
        self.assertEqual(coll.count(), 0)

    def test_on_non_existant_collection(self):
        client = self._get_test_client()

        coll = client.collection('things')
        self.assertEqual(coll.count(), 0)
