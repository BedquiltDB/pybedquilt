import testutils
import json
import string
import psycopg2


class TestSaveDocuments(testutils.BedquiltTestCase):

    def test_save_into_non_existant_collection(self):
        client = self._get_test_client()
        coll = client['things']

        _ = coll.save({"_id": "aaa", "a": 1})

        self.assertEqual(
            list(coll.find()),
            [{'_id': 'aaa', 'a': 1}])

    def test_save_with_no_id(self):
        client = self._get_test_client()
        coll = client['things']

        client.create_collection('things')

        doc = {
            "name": "spanner"
        }
        coll.save(doc)

        result = list(coll.find())

        self.assertEqual(len(result), 1)
        d = result[0]
        self.assertEqual(set(d.keys()),
                         set(doc.keys()).union(set(["_id"])))

        self.assertEqual(d['name'], 'spanner')

    def test_save_overwriting_doc(self):
        client = self._get_test_client()
        coll = client['things']

        client.create_collection('things')

        dud = {
            '_id': 'dud',
            'name': 'dud'}
        doc = {
            "_id": "aaa",
            "name": "spanner"
        }
        coll.insert(dud)
        coll.insert(doc)

        result = list(coll.find())
        self.assertEqual(result,
                         [
                             dud,
                             doc
                         ])

        # Mutate and save
        doc['name'] = 'fish'
        doc['color'] = 'blue'

        coll.save(doc)

        result = list(coll.find())
        self.assertEqual(result,
                         [
                             dud,
                             doc
                         ])

        # Mutate and save again
        doc['name'] = 'trout'
        doc['color'] = 'pink'
        doc['count'] = 22

        coll.save(doc)

        result = list(coll.find())
        self.assertEqual(result,
                         [
                             dud,
                             doc
                         ])
