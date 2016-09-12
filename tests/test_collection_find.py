import testutils
import json
import string
import psycopg2
import pybedquilt
import random
import time


class TestFindDocuments(testutils.BedquiltTestCase):

    def test_find_on_empty_collection(self):
        client = self._get_test_client()
        coll = client['people']

        queries = [
            {},
            {"likes": ["icecream"]},
            {"name": "Mike"},
            {"_id": "mike"},
            {"name": {"$regex": ".*wat.*"}},
            {"name": {"$noteq": "Mike"}}
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
        result = coll.find_one({'age': {'$eq': 32}})
        self.assertEqual(result, mike)

        # find no-one
        result = coll.find_one({'name': 'XXXXX'})
        self.assertEqual(result, None)

        result = coll.find_one({'name': {'$notin': ['Sarah', 'Mike']}})
        self.assertEqual(result, None)

    def test_find_one_with_skip_and_sort(self):
        client = self._get_test_client()
        coll = client['things']

        rows = [
            {'_id': 'a', 'n': 3, 'color': 'red'},
            {'_id': 'b', 'n': 1, 'color': 'red'},
            {'_id': 'c', 'n': 3, 'color': 'blue'},
            {'_id': 'd', 'n': 2, 'color': 'blue'}
        ]
        for row in rows:
            coll.save(row)

        result = coll.find_one({'color': 'blue'}, sort=[{'n': 1}])
        self.assertEqual(result['_id'], 'd')

        result = coll.find_one({'color': 'blue'}, sort=[{'n': 1}], skip=1)
        self.assertEqual(result['_id'], 'c')

        result = coll.find_one({'color': 'blue'}, sort=[{'n': 1}], skip=2)
        self.assertEqual(result, None)

        result = coll.find_one({'color': 'blue'}, sort=[{'n': -1}])
        self.assertEqual(result['_id'], 'c')

        result = coll.find_one({}, sort=[{'n': 1}])
        self.assertEqual(result['_id'], 'b')

    def test_find_special_queries(self):
        client = self._get_test_client()
        coll = client['things']

        rows = [
            {'_id': 'a', 'n': 3, 'color': 'red'},
            {'_id': 'b', 'n': 1, 'color': 'red'},
            {'_id': 'c', 'n': 3, 'color': 'blue'},
            {'_id': 'd', 'n': 2, 'color': 'blue'}
        ]
        for row in rows:
            coll.save(row)

        result = coll.find_one({'color': 'blue', 'n': {'$gt': 2}})
        self.assertEqual(result['_id'], 'c')

        result = list(coll.find({'color': {'$regex': 'bl.*'}}))
        self.assertEqual(len(result), 2)
        self.assertEqual(list(map(lambda d: d['_id'], result)), ['c', 'd'])

        result = coll.count({'color': {'$type': 'number'}})
        self.assertEqual(result, 0)

    def test_find_many_by_ids(self):
        client = self._get_test_client()
        coll = client['things']
        rows = [
            {'_id': 'a'},
            {'_id': 'b'},
            {'_id': 'c'},
            {'_id': 'd'}
        ]
        for row in rows:
            coll.insert(row)

        result = list(coll.find_many_by_ids(['b', 'c', 'wat']))
        self.assertEqual(list(map(lambda r: r['_id'], result)), ['b', 'c'])

        result = list(coll.find_many_by_ids(['wat']))
        self.assertEqual(list(map(lambda r: r['_id'], result)), [])

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

    def test_many_by_ids(self):
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
        jim = {'_id': "jim@example.com",
                'name': "Jim",
                'age': 32,
                'likes': ['fishing', 'crochet']}

        coll.insert(sarah)
        coll.insert(mike)
        coll.insert(jim)

        # sarah and jim
        result = list(
            coll.find_many_by_ids(['sarah@example.com', 'jim@example.com'])
        )
        self.assertEqual(result, [sarah, jim])

        # sarah and mike
        result = list(
            coll.find_many_by_ids(['sarah@example.com', 'mike@example.com'])
        )
        self.assertEqual(result, [sarah, mike])

        # mike and no-one
        result = list(
            coll.find_many_by_ids(['no-one', 'mike@example.com'])
        )
        self.assertEqual(result, [mike])

        # no match
        result = list(
            coll.find_many_by_ids(['wat'])
        )
        self.assertEqual(result, [])


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
                'name': "Darren O'Reilly",
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

        result = coll.find({'name': "Darren O'Reilly"})
        self.assertEqual(list(result), [darren])

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
            result = coll.find(q, sort=[{'age': 1}])
            self.assertEqual(list(result), [])

    def test_sort_on_two_fields(self):
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
                'age': 20,
                'city': "Manchester"}

        coll.insert(sarah)
        coll.insert(mike)
        coll.insert(jill)
        coll.insert(darren)

        # age ascending, name ascending
        result = coll.find(sort=[{'age': 1}, {'name': 1}])
        names = list(map(lambda x: x['name'], result))
        self.assertEqual(names, ['Darren', 'Jill', 'Mike', 'Sarah'])

        # age descending, name ascending
        result = coll.find(sort=[{'age': -1}, {'name': 1}])
        names = list(map(lambda x: x['name'], result))
        self.assertEqual(names, ['Sarah', 'Jill', 'Mike', 'Darren'])

        # age ascending, name descending
        result = coll.find(sort=[{'age': 1}, {'name': -1}])
        names = list(map(lambda x: x['name'], result))
        self.assertEqual(names, ['Darren', 'Mike', 'Jill', 'Sarah'])

        # age descending, name descending
        result = coll.find(sort=[{'age': -1}, {'name': -1}])
        names = list(map(lambda x: x['name'], result))
        self.assertEqual(names, ['Sarah', 'Mike', 'Jill', 'Darren'])

        # age, then $created
        result = coll.find(sort=[{'age': 1}, {'$created': 1}])
        names = list(map(lambda x: x['name'], result))
        self.assertEqual(names, ['Darren', 'Mike', 'Jill', 'Sarah'])

        # age, then $created descending
        result = coll.find(sort=[{'age': 1}, {'$created': -1}])
        names = list(map(lambda x: x['name'], result))
        self.assertEqual(names, ['Darren', 'Jill', 'Mike', 'Sarah'])

        # age, then $updated descending
        result = coll.find(sort=[{'age': 1}, {'$updated': -1}])
        names = list(map(lambda x: x['name'], result))
        self.assertEqual(names, ['Darren', 'Jill', 'Mike', 'Sarah'])
        # update mike record
        mike['wat'] = True
        time.sleep(0.1)
        coll.save(mike)
        result = coll.find(sort=[{'age': 1}, {'$updated': -1}])
        names = list(map(lambda x: x['name'], result))
        self.assertEqual(names, ['Darren', 'Mike', 'Jill', 'Sarah'])


    def test_find_existing_documents_with_sort(self):
        client = self._get_test_client()
        coll = client['people']

        # seed data
        docs = []
        for x in range(50):
            docs.append({
                '_id': str(random.random())[2:],
                'color': 'red',
                'n': x
            })
        for x in range(50, 100):
            docs.append({
                '_id': str(random.random())[2:],
                'color': 'blue',
                'n': x
            })
        random.shuffle(docs)
        for doc in docs:
            coll.insert(doc)

        # with sort ascending on n
        result = coll.find(sort=[{'n': 1}])
        nums = list(map(lambda x: x['n'], result))
        self.assertEqual(nums, sorted(nums))

        # with sort descending on n
        result = coll.find(sort=[{'n': -1}])
        nums = list(map(lambda x: x['n'], result))
        self.assertEqual(nums, sorted(nums, reverse=True))

        # ascending, skip 2, limit 5
        result = coll.find(sort=[{'n': 1}], skip=2, limit=5)
        nums = list(map(lambda x: x['n'], result))
        self.assertEqual(nums, [
            2, 3, 4, 5, 6
        ])

        # descending, skip 2, limit 5
        result = coll.find(sort=[{'n': -1}], skip=2, limit=5)
        nums = list(map(lambda x: x['n'], result))
        self.assertEqual(nums, [
            97, 96, 95, 94, 93
        ])

        # descending, no skip, limit 3
        result = coll.find(sort=[{'n': -1}], limit=3)
        nums = list(map(lambda x: x['n'], result))
        self.assertEqual(nums, [
            99, 98, 97
        ])

        # only blue, ascending
        result = coll.find({'color': 'blue'}, sort=[{'n': 1}])
        nums = list(map(lambda x: x['n'], result))
        self.assertEqual(nums, sorted(nums))
        self.assertEqual(len(nums), 50)

        # only blue, descecnding, skip 10, limit 2
        result = coll.find(sort=[{'n': -1}], skip=10, limit=2)
        nums = list(map(lambda x: x['n'], result))
        self.assertEqual(nums, [
            89, 88
        ])
