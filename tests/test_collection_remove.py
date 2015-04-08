import testutils
import json
import string


class TestRemoveDocumnts(testutils.BedquiltTestCase):

    def test_remove_on_empty_collection(self):
        client = self._get_test_client()
        coll = client['people']

        client.create_collection('people')

        result = coll.remove({'age': 22})
        self.assertEqual(result, 0)

    def test_remove_one_on_empty_collection(self):
        client = self._get_test_client()
        coll = client['people']

        client.create_collection('people')

        result = coll.remove_one({'age': 22})
        self.assertEqual(result, 0)

    def test_remove_on_non_existant_collection(self):
        client = self._get_test_client()
        coll = client['people']

        result = coll.remove({'age': 22})
        self.assertEqual(result, 0)

    def test_remove_one_on_non_existant_collection(self):
        client = self._get_test_client()
        coll = client['people']

        result = coll.remove_one({'age': 22})
        self.assertEqual(result, 0)

    def test_remove_hitting_single_document(self):
        client = self._get_test_client()
        coll = client['people']

        sarah = {'_id': "sarah@example.com",
                 'name': "Sarah",
                 'city': "Glasgow",
                 'age': 34,
                 'likes': ['icecream', 'cats']}
        mike = {'_id': "mike@example.com",
                'name': "Mike",
                'city': "Edinburgh",
                'age': 32,
                'likes': ['cats', 'crochet']}
        jill = {'_id': "jill@example.com",
                'name': "Jill",
                'city': "Glasgow",
                'age': 32,
                'likes': ['code', 'crochet']}
        darren = {'_id': "darren@example.com",
                'name': "Darren",
                'city': "Manchester"}

        coll.insert(sarah)
        coll.insert(mike)
        coll.insert(jill)
        coll.insert(darren)

        result = coll.remove({'age': 34})

        self.assertEqual(result, 1)

        result = coll.find({})
        self.assertEqual(result,
                         [
                             mike,
                             jill,
                             darren
                         ])

    def test_remove_hitting_many_document(self):
        client = self._get_test_client()
        coll = client['people']

        sarah = {'_id': "sarah@example.com",
                 'name': "Sarah",
                 'city': "Glasgow",
                 'age': 34,
                 'likes': ['icecream', 'cats']}
        mike = {'_id': "mike@example.com",
                'name': "Mike",
                'city': "Edinburgh",
                'age': 32,
                'likes': ['cats', 'crochet']}
        jill = {'_id': "jill@example.com",
                'name': "Jill",
                'city': "Glasgow",
                'age': 32,
                'likes': ['code', 'crochet']}
        darren = {'_id': "darren@example.com",
                'name': "Darren",
                'city': "Manchester"}

        coll.insert(sarah)
        coll.insert(mike)
        coll.insert(jill)
        coll.insert(darren)

        result = coll.remove({'age': 32})

        self.assertEqual(result, 2)

        result = coll.find({})
        self.assertEqual(result,
                         [
                             sarah,
                             darren
                         ])

    def test_remove_one_documents(self):
        client = self._get_test_client()
        coll = client['people']

        sarah = {'_id': "sarah@example.com",
                 'name': "Sarah",
                 'city': "Glasgow",
                 'age': 34,
                 'likes': ['icecream', 'cats']}
        mike = {'_id': "mike@example.com",
                'name': "Mike",
                'city': "Edinburgh",
                'age': 32,
                'likes': ['cats', 'crochet']}
        jill = {'_id': "jill@example.com",
                'name': "Jill",
                'city': "Glasgow",
                'age': 32,
                'likes': ['code', 'crochet']}
        darren = {'_id': "darren@example.com",
                'name': "Darren",
                'city': "Manchester"}

        coll.insert(sarah)
        coll.insert(mike)
        coll.insert(jill)
        coll.insert(darren)

        # remove_one a single document matching a wide query
        result = coll.remove_one({'age': 32})
        self.assertEqual(result, 1)

        result = coll.find()
        self.assertEqual(result,
                         [
                             sarah,
                             jill,
                             darren
                         ])

        # remove_one a single document matching a specific query
        result = coll.remove_one({'name': 'Darren'})
        self.assertEqual(result, 1)

        result = coll.find()
        self.assertEqual(result,
                         [
                             sarah,
                             jill
                         ])

        # remove_one a single document matching an _id
        result = coll.remove({'_id': 'jill@example.com'})
        self.assertEqual(result, 1)

        result = coll.find()
        self.assertEqual(result,
                         [
                             sarah
                         ])

    def test_remove_one_by_id_on_non_existant_collection(self):
        client = self._get_test_client()
        coll = client['people']

        result = coll.remove_one_by_id('jill@example.com')
        self.assertEqual(result, 0)

    def test_remove_one_by_id_on_empty_collection(self):
        client = self._get_test_client()
        coll = client['people']

        client.create_collection('people')

        result = coll.remove_one_by_id('jill@example.com')
        self.assertEqual(result, 0)

    def test_remove_one_by_id(self):
        client = self._get_test_client()
        coll = client['people']

        sarah = {'_id': "sarah@example.com",
                 'name': "Sarah",
                 'city': "Glasgow",
                 'age': 34,
                 'likes': ['icecream', 'cats']}
        mike = {'_id': "mike@example.com",
                'name': "Mike",
                'city': "Edinburgh",
                'age': 32,
                'likes': ['cats', 'crochet']}
        jill = {'_id': "jill@example.com",
                'name': "Jill",
                'city': "Glasgow",
                'age': 32,
                'likes': ['code', 'crochet']}
        darren = {'_id': "darren@example.com",
                'name': "Darren",
                'city': "Manchester"}

        coll.insert(sarah)
        coll.insert(mike)
        coll.insert(jill)
        coll.insert(darren)

        # remove an existing document
        result = coll.remove_one_by_id('jill@example.com')
        self.assertEqual(result, 1)

        result = coll.find()
        self.assertEqual(result,
                         [
                             sarah,
                             mike,
                             darren
                         ])

        # remove a document which is not in collection
        result = coll.remove_one_by_id('jill@example.com')
        self.assertEqual(result, 0)

        result = coll.find()
        self.assertEqual(result,
                         [
                             sarah,
                             mike,
                             darren
                         ])
