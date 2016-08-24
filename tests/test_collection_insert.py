import testutils
import json
import string
import psycopg2
import six


class TestInsertDocument(testutils.BedquiltTestCase):

    def test_insert_into_non_existant_collection(self):
        client = self._get_test_client()
        coll = client['people']

        doc = {
            "_id": "user@example.com",
            "name": "Some User",
            "age": 20
        }

        result = coll.insert(doc)

        self.assertEqual(
            result, 'user@example.com'
        )

        collections = client.list_collections()
        self.assertEqual(collections, ["people"])

    def test_with_non_string_id(self):
        client = self._get_test_client()
        coll = client['things']

        docs = [
            {
                "_id": 42,
                "name": "Penguin",
                "age": "penguin@example.com"
            },
            {
                "_id": ['derp'],
                "name": "Penguin",
                "age": "penguin@example.com"
            },
            {
                "_id": {"name": "Penguin"},
                "age": "penguin@example.com"
            },
            {
                "_id": False,
                "name": "Penguin",
                "age": "penguin@example.com"
            },
            {
                "_id": None,
                "name": "Penguin",
                "age": "penguin@example.com"
            }
        ]
        for doc in docs:
            with self.assertRaises(psycopg2.InternalError):
                coll.insert(doc)

    def test_insert_without_id(self):
        client = self._get_test_client()
        coll = client['people']

        doc = {
            "name": "Some User",
            "age": 20
        }
        result = coll.insert(doc)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, six.string_types))

        self.assertEqual(len(list(result)), 24)
        for character in result:
            self.assertIn(character, string.hexdigits)

    def test_insert_with_repeat_id(self):
        client = self._get_test_client()
        coll = client['people']

        doc = {
            "_id": "user_one",
            "name": "Some User",
            "age": 20
        }

        result = coll.insert(doc)

        self.assertEqual(result, "user_one")

        with self.assertRaises(psycopg2.IntegrityError):
            result = coll.insert(doc)

        result = coll.find()
        self.assertEqual(len(list(result)), 1)
