import pybedquilt
import testutils


class TestBedquiltCollection(testutils.BedquiltTestCase):

    def test_bedquilt_collection(self):
        client = pybedquilt.BedquiltClient(
            'dbname={}'.format(self.database_name))
        coll = client['things']

        methods = ['insert',
                   'save',
                   'find',
                   'find_one',
                   'find_one_by_id',
                   'remove',
                   'remove_one',
                   'remove_one_by_id']

        for method in methods:
            self.assertTrue(hasattr(coll, method))
            self.assertTrue(callable(coll.__getattribute__(method)))

        self.assertTrue(hasattr(coll, 'client'))
        self.assertIsInstance(coll.client, pybedquilt.BedquiltClient)
        self.assertEqual(coll.client, client)

        self.assertTrue(hasattr(coll, 'collection_name'))
        self.assertEqual(coll.collection_name, 'things')
