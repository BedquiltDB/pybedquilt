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

    def test_simple_scenario(self):
        client = self._get_test_client()
        coll = client.collection('things')

        coll.insert({'_id': 'spanner', 'type': 'tool'})
        coll.insert({'_id': 'hammer', 'type': 'tool'})
        coll.insert({'_id': 'screwdriver', 'type': 'tool'})

        coll.insert({'_id': 'crow', 'type': 'bird'})
        coll.insert({'_id': 'sparrow', 'type': 'bird'})
        coll.insert({'_id': 'weasel', 'type': 'animal'})

        self.assertEqual(coll.count(), 6)
        self.assertEqual(coll.count({'type': 'tool'}), 3)
        self.assertEqual(coll.count({'type': 'bird'}), 2)
        self.assertEqual(coll.count({'_id': 'crow'}), 1)
