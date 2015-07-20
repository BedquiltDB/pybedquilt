import testutils
import json
import string
import psycopg2


class TestFindDocuments(testutils.BedquiltTestCase):

    def test_find_on_empty_collection(self):
        client = self._get_test_client()
        coll = client['people']

        queries = [
            {},
            {"likes": ["icecream"]},
            {"name": "Mike"},
            {"_id": "mike"}
        ]

        for q in queries:
            # find_one
            result = coll.find_one(q)
            self.assertEqual(result, None)

            # find
            result = coll.find_one(q)
            self.assertEqual(result, None)

    def test_find_one_existing_document(self):
        client = self._get_test_client()
        coll = client['people']

        sarah = {'_id': "sarah@example.com",
                 'name': "Sarah",
                 'age': 34,
                 'likes': ['icecream', 'cats']}
        mike = {'_id': "mike@example.com",
                'name': "Mike",
                'age': 32,
                'likes': ['cats', 'crochet']}

        coll.insert(sarah)
        coll.insert(mike)

        # find sarah
        result = coll.find_one({'name': 'Sarah'})
        self.assertEqual(result, sarah)

        # find mike
        result = coll.find_one({'name': 'Mike'})
        self.assertEqual(result, mike)

        # find no-one
        result = coll.find_one({'name': 'XXXXX'})
        self.assertEqual(result, None)

    def test_find_one_by_id(self):
        client = self._get_test_client()
        coll = client['people']

        sarah = {'_id': "sarah@example.com",
                 'name': "Sarah",
                 'age': 34,
                 'likes': ['icecream', 'cats']}
        mike = {'_id': "mike@example.com",
                'name': "Mike",
                'age': 32,
                'likes': ['cats', 'crochet']}

        coll.insert(sarah)
        coll.insert(mike)

        # find sarah
        result = coll.find_one_by_id('sarah@example.com')
        self.assertEqual(result, sarah)

        # find mike
        result = coll.find_one_by_id('mike@example.com')
        self.assertEqual(result, mike)

        # find no-one
        result = coll.find_one_by_id('XXXXX')
        self.assertEqual(result, None)

    def test_find_existing_documents(self):
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

        # find matching an _id
        result = coll.find({'_id': 'jill@example.com'})
        self.assertEqual(list(result), [jill])

        # find by match on the city field
        result = coll.find({'city': 'Glasgow'})
        self.assertEqual(list(result), [sarah, jill])

        result = coll.find({'city': 'Edinburgh'})
        self.assertEqual(list(result), [mike])

        result = coll.find({'city': 'Manchester'})
        self.assertEqual(list(result), [darren])

        result = coll.find({'city': 'New York'})
        self.assertEqual(list(result), [])

        # find all
        result = coll.find()
        self.assertEqual(list(result),
                         [
                             sarah,
                             mike,
                             jill,
                             darren,
                         ])
