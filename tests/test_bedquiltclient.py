import pybedquilt
import testutils
import psycopg2


class TestBedquiltClient(testutils.BedquiltTestCase):

    def test_create_client_by_dsn(self):
        client = pybedquilt.BedquiltClient(
            'dbname={}'.format(self.database_name))

        self.assertIsNotNone(client)
        self.assertTrue(hasattr(client, 'collection'))

    def test_create_client_with_connection(self):
        conn = psycopg2.connect('dbname={}'.format(self.database_name))
        client = pybedquilt.BedquiltClient(connection=conn)

        self.assertIsNotNone(client)
        self.assertTrue(hasattr(client, 'collection'))

    def test_create_client_with_kwargs(self):
        client = pybedquilt.BedquiltClient(dbname=self.database_name)

        self.assertIsNotNone(client)
        self.assertTrue(hasattr(client, 'collection'))

    def test_get_collection_function(self):
        client = self._get_test_client()

        coll = client.collection('things')
        self.assertIsNotNone(coll)

        self.assertIsInstance(coll, pybedquilt.BedquiltCollection)
        self.assertEqual(coll.collection_name, 'things')
        self.assertTrue(coll.client is client)

    def test_get_collection_square_brackets(self):
        client = self._get_test_client()

        coll = client['stuff']
        self.assertIsNotNone(coll)

        self.assertIsInstance(coll, pybedquilt.BedquiltCollection)
        self.assertEqual(coll.collection_name, 'stuff')
        self.assertTrue(coll.client is client)

    def test_create_collection(self):
        client = self._get_test_client()

        result = client.create_collection('one')
        self.assertTrue(result)
        result = client.create_collection('one')
        self.assertFalse(result)

    def test_list_collections(self):
        client = self._get_test_client()

        # Empty
        collections = client.list_collections()
        self.assertEqual(len(collections), 0)

        # One collection
        client.create_collection('one')

        collections = client.list_collections()
        self.assertEqual(len(collections), 1)
        self.assertEqual(collections, ['one'])

        # Two collections
        client.create_collection('two')

        collections = client.list_collections()
        self.assertEqual(len(collections), 2)
        self.assertEqual(set(collections), set(['one', 'two']))

    def test_delete_collection(self):
        client = self._get_test_client()

        # Delete non-existant
        result = client.delete_collection('non')
        self.assertFalse(result)

        # existant
        client.create_collection('one')
        result = client.delete_collection('one')
        self.assertTrue(result)
        result = client.delete_collection('one')
        self.assertFalse(result)

        names = ['one', 'two', 'three']

        for name in names:
            client.create_collection(name)

        self.assertEqual(client.list_collections(), names)

        for name in names:
            client.delete_collection(name)

        self.assertEqual(client.list_collections(), [])
