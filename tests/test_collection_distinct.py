import testutils
import json
import string
import psycopg2


class TestCollectionCount(testutils.BedquiltTestCase):

    def test_on_empty_collection(self):
        client = self._get_test_client()
        client.create_collection('things')

        coll = client.collection('things')
        result = coll.distinct('name')
        self.assertEqual(list(result), [])

    def test_on_non_existant_collection(self):
        client = self._get_test_client()

        coll = client.collection('things')
        result = coll.distinct('name')
        self.assertEqual(list(result), [])

    def test_distinct_on_realistic_example(self):
        client = self._get_test_client()

        coll = client.collection('things')

        docs = [
            {'name': 'Sarah', 'age': 22},
            {'name': 'Brian'},
            {'name': 'Mike', 'age': 30},
            {'name': 'Diane', 'age': 38},
            {'name': 'Peter', 'age': 30}
        ]
        for doc in docs:
            coll.insert(doc)

        result = coll.distinct('age')
        self.assertEqual(
            sorted(list(result)),
            sorted([22, 30, 38, None])
        )

    def test_distinct_on_dotted_path(self):
        client = self._get_test_client()

        coll = client.collection('things')

        docs = [
            {'name': 'Sarah', 'address': {'city': 'Edinburgh'}},
            {'name': 'Brian', 'address': {'city': 'London'}},
            {'name': 'Mike', 'address': {'city': 'Edinburgh'}},
            {'name': 'Diane', 'address': {'city': 'Manchester'}},
            {'name': 'Peter', 'address': {'city': 'Edinburgh'}}
        ]
        for doc in docs:
            coll.insert(doc)

        result = coll.distinct('address.city')
        self.assertEqual(
            sorted(list(result)),
            sorted(['London', 'Edinburgh', 'Manchester'])
        )
