import testutils
import json
import string
import psycopg2
import pybedquilt
import random


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
            # find
            result = coll.find(q)
            self.assertEqual(list(result), [])

            # find_one
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
        result = list(coll.find())
        self.assertEqual(result,
                         [
                             sarah,
                             mike,
                             jill,
                             darren,
                         ])


        # find streaming
        result = coll.find()
        self.assertEqual(type(result), pybedquilt.BedquiltCursor)
        count = 0
        for doc in result:
            count += 1
            self.assertIsNotNone(doc)
            self.assertEqual(type(doc), dict)

        self.assertEqual(count, 4)


class TestFindWithSkipAndLimit(testutils.BedquiltTestCase):

    def test_on_empty_collection(self):
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
            result = coll.find(q, skip=1, limit=2)
            self.assertEqual(list(result), [])

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

        # find with limit
        result = coll.find({}, limit=2)
        self.assertEqual(list(result), [sarah, mike])

        # find with skip and limit
        result = coll.find({}, skip=1, limit=2)
        self.assertEqual(list(result), [mike, jill])

        # only skip
        result = coll.find({}, skip=2)
        self.assertEqual(list(result), [jill, darren])

        # limit with a query
        result = coll.find({'city': 'Glasgow'}, limit=1)
        self.assertEqual(list(result), [sarah])


class TestFindWithSort(testutils.BedquiltTestCase):

    def test_on_empty_collection(self):
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
            result = coll.find(q, sort={'age': 1})
            self.assertEqual(list(result), [])

    def test_find_existing_documents_with_sort(self):
        client = self._get_test_client()
        coll = client['people']

        # seed data
        docs = []
        for x in range(100):
            docs.append({
                '_id': str(random.random())[2:],
                'n': x
            })
        random.shuffle(docs)
        for doc in docs:
            coll.insert(doc)

        # with sort ascending on n
        result = coll.find(sort={'n': 1})
        nums = map(lambda x: x['n'], result)
        self.assertEqual(nums, sorted(nums))

        # with sort descending on n
        result = coll.find(sort={'n': -1})
        nums = map(lambda x: x['n'], result)
        self.assertEqual(nums, sorted(nums, reverse=True))

        # ascending, skip 2, limit 5
        result = coll.find(sort={'n': 1}, skip=2, limit=5)
        nums = map(lambda x: x['n'], result)
        self.assertEqual(nums, [
            2, 3, 4, 5, 6
        ])

        # descending, skip 2, limit 5
        result = coll.find(sort={'n': -1}, skip=2, limit=5)
        nums = map(lambda x: x['n'], result)
        self.assertEqual(nums, [
            97, 96, 95, 94, 93
        ])
