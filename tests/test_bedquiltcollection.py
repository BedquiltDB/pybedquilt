import pybedquilt
import testutils


class TestBedquiltCollection(testutils.BedquiltTestCase):

    def test_bedquilt_collection(self):
        client = pybedquilt.BedquiltClient(
            'dbname={}'.format(self.database_name))
        coll = client['things']

        self.assertTrue(hasattr(coll, 'client'))
        self.assertTrue(hasattr(coll, 'collection_name'))
        self.assertTrue(hasattr(coll, 'find'))
        self.assertTrue(hasattr(coll, 'insert'))
