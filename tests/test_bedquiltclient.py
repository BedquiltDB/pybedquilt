import pybedquilt
import testutils


class TestBedquiltClient(testutils.BedquiltTestCase):

    def test_create_client_by_dsn(self):
        client = pybedquilt.BedquiltClient(
            'dbname={}'.format(self.database_name))

        self.assertIsNotNone(client)
        self.assertTrue(hasattr(client, 'collection'))

    def test_get_collection_function(self):
        client = self._get_test_client()

        coll = client.collection('things')
        self.assertIsNotNone(coll)

        self.assertIsInstance(coll, pybedquilt.BedquiltCollection)
        self.assertEqual(coll.collection_name, 'things')

    def test_get_collection_square_brackets(self):
        client = self._get_test_client()

        coll = client['stuff']
        self.assertIsNotNone(coll)

        self.assertIsInstance(coll, pybedquilt.BedquiltCollection)
        self.assertEqual(coll.collection_name, 'stuff')
