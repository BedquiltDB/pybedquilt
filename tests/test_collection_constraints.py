import testutils
import json
import string
import psycopg2


def _test_constraint(test, coll, spec):
    result = coll.add_constraints(spec['constraints'])
    test.assertEqual(result, True)

    result = coll.add_constraints(spec['constraints'])
    test.assertEqual(result, False)

    for current in spec['tests']:
        if callable(current):
            current()
            continue
        data = current[0]
        expected_result = current[1]
        test._test_save(coll, data, expected_result)


class TestAddRequiredConstraint(testutils.BedquiltTestCase):

    def test_add_simple_required_constraint(self):
        client = self._get_test_client()
        coll = client['people']

        spec = {
            'constraints': {'name': {'$required': 1}},
            'tests': [
                ({
                    '_id': 'paul@example.com',
                    'age': 20
                 },
                 psycopg2.IntegrityError),
                ({
                    '_id': 'paul@example.com',
                    'name': None,
                    'age': 20
                 },
                 'paul@example.com'),
                ({
                    '_id': 'paul@example.com',
                    'name': 'Paul',
                    'age': 20
                 },
                 'paul@example.com'),
            ]
        }
        _test_constraint(self, coll, spec)

    def test_required_at_nested_path(self):
        client = self._get_test_client()
        coll = client['people']

        spec = {
            'constraints': {'address.city': {'$required': 1}},
            'tests': [
                ({
                    '_id': 'paul@example.com',
                    'age': 20
                 },
                 psycopg2.IntegrityError),
                ({
                    '_id': 'paul@example.com',
                    'age': 20,
                    'address': {
                        'street': 'wat'
                    }
                 },
                 psycopg2.IntegrityError),
                ({
                    '_id': 'paul@example.com',
                    'name': None,
                    'age': 20,
                    'address': {
                        'street': 'wat',
                        'city': None
                    }
                 },
                 'paul@example.com'),
                ({
                    '_id': 'paul@example.com',
                    'name': 'Paul',
                    'age': 20,
                    'address': {
                        'street': 'wat',
                        'city': 'London'
                    }
                 },
                 'paul@example.com')
            ]
        }
        _test_constraint(self, coll, spec)

    def test_required_at_nested_array_path(self):
        client = self._get_test_client()
        coll = client['people']

        spec = {
            'constraints': {'addresses.0.city': {'$required': 1}},
            'tests': [
                ({
                    '_id': 'paul@example.com',
                    'age': 20
                 },
                 psycopg2.IntegrityError),
                ({
                    '_id': 'paul@example.com',
                    'age': 20,
                    'addresses': []
                 },
                 psycopg2.IntegrityError),
                ({
                    '_id': 'paul@example.com',
                    'age': 20,
                    'addresses': [
                        {'street': 'wat'}
                    ]
                 },
                 psycopg2.IntegrityError),
                ({
                    '_id': 'paul@example.com',
                    'name': None,
                    'age': 20,
                    'addresses': [
                        {'street': 'wat',
                         'city': None}
                    ]
                 },
                 'paul@example.com'),
                ({
                    '_id': 'paul@example.com',
                    'name': 'Paul',
                    'age': 20,
                    'addresses': [
                        {'street': 'wat',
                         'city': 'London'}
                    ]
                 },
                 'paul@example.com')
            ]
        }

        _test_constraint(self, coll, spec)


    def test_removing_required_constraint(self):
        client = self._get_test_client()
        coll = client['people']

        spec = {
            'constraints': {'name': {'$required': 1}},
            'tests': [
                ({
                    '_id': 'paul@example.com',
                    'age': 20
                 },
                 psycopg2.IntegrityError),
                ({
                    '_id': 'paul@example.com',
                    'name': 'Paul',
                    'age': 20
                 },
                 'paul@example.com'),
                lambda: coll.remove({}),
                lambda: coll.remove_constraints({
                    'name': {'$required': 1}}),
                ({
                    '_id': 'paul@example.com',
                    'age': 20
                 },
                 'paul@example.com'),
                ({
                    '_id': 'paul@example.com',
                    'name': 'Paul',
                    'age': 20
                 },
                 'paul@example.com')
            ]
        }
        _test_constraint(self, coll, spec)


class TestNotNullConstraint(testutils.BedquiltTestCase):

    def test_simple_notnull_constraint(self):
        client = self._get_test_client()
        coll = client['people']

        spec = {
            'constraints': {'name': {'$notnull': 1}},
            'tests': [
                ({
                    '_id': 'paul@example.com',
                    'name': None
                 },
                 psycopg2.IntegrityError),
                ({
                    '_id': 'paul@example.com',
                    'name': 'paul'
                 },
                 'paul@example.com'),
                ({
                    '_id': 'paul@example.com',
                    'age': 20
                 },
                 'paul@example.com')
            ]
        }

        _test_constraint(self, coll, spec)

    def test_notnull_on_nested_path(self):
        client = self._get_test_client()
        coll = client['people']

        spec = {
            'constraints': {'address.city': {'$notnull': 1}},
            'tests': [
                ({
                    '_id': 'paul@example.com',
                    'name': None
                 },
                 'paul@example.com'),
                ({
                    '_id': 'paul@example.com',
                    'name': 'paul',
                    'address': {
                        'street': 'wat'
                    }
                 },
                 'paul@example.com'),
                ({
                    '_id': 'paul@example.com',
                    'name': 'paul',
                    'address': {
                        'street': 'wat',
                        'city': 'here'
                    }
                 },
                 'paul@example.com'),
                ({
                    '_id': 'paul@example.com',
                    'name': 'paul',
                    'address': {
                        'street': 'wat',
                        'city': None

                    }
                 },
                 psycopg2.IntegrityError),
            ]
        }

        _test_constraint(self, coll, spec)

    def test_notnull_on_nested_array_path(self):
        client = self._get_test_client()
        coll = client['people']

        spec = {
            'constraints': {'addresses.0.city': {'$notnull': 1}},
            'tests': [
                ({
                    '_id': 'paul@example.com',
                    'name': None
                 },
                 'paul@example.com'),
                ({
                    '_id': 'paul@example.com',
                    'name': 'paul',
                    'addresses':[
                        {'street': 'wat'}
                    ]
                 },
                 'paul@example.com'),
                ({
                    '_id': 'paul@example.com',
                    'name': 'paul',
                    'addresses':[
                        {'street': 'wat',
                         'city': 'here'}
                    ]
                 },
                 'paul@example.com'),
                ({
                    '_id': 'paul@example.com',
                    'name': 'paul',
                    'addresses':[
                        {'street': 'wat',
                         'city': None}
                    ]
                 },
                 psycopg2.IntegrityError),
            ]
        }

        _test_constraint(self, coll, spec)

class TestTypeConstraint(testutils.BedquiltTestCase):

    def test_simple_type_constraint(self):
        client = self._get_test_client()
        coll = client['people']

        spec = {
            'constraints': {'name': {'$type': 'string'}},
            'tests': [
                ({
                    '_id': 'paul@example.com',
                    'name': 42
                 },
                 psycopg2.IntegrityError),
                ({
                    '_id': 'paul@example.com',
                    'name': 'paul'
                 },
                 'paul@example.com'),
                ({
                    '_id': 'paul@example.com',
                    'age': 20
                 },
                 'paul@example.com')
            ]
        }

        _test_constraint(self, coll, spec)

    def test_type_on_nested_path(self):
        client = self._get_test_client()
        coll = client['people']

        spec = {
            'constraints': {'address.city': {'$type': 'string'}},
            'tests': [
                ({
                    '_id': 'paul@example.com',
                    'name': None
                 },
                 'paul@example.com'),
                ({
                    '_id': 'paul@example.com',
                    'name': 'paul',
                    'address': {
                        'street': 'wat'
                    }
                 },
                 'paul@example.com'),
                ({
                    '_id': 'paul@example.com',
                    'name': 'paul',
                    'address': {
                        'street': 'wat',
                        'city': 'here'
                    }
                 },
                 'paul@example.com'),
                ({
                    '_id': 'paul@example.com',
                    'name': 'paul',
                    'address': {
                        'street': 'wat',
                        'city': 42

                    }
                 },
                 psycopg2.IntegrityError),
            ]
        }

        _test_constraint(self, coll, spec)

    def test_type_on_nested_array_path(self):
        client = self._get_test_client()
        coll = client['people']

        spec = {
            'constraints': {'addresses.0.city': {'$type': 'string'}},
            'tests': [
                ({
                    '_id': 'paul@example.com',
                    'name': None
                 },
                 'paul@example.com'),
                ({
                    '_id': 'paul@example.com',
                    'name': 'paul',
                    'addresses':[
                        {'street': 'wat'}
                    ]
                 },
                 'paul@example.com'),
                ({
                    '_id': 'paul@example.com',
                    'name': 'paul',
                    'addresses':[
                        {'street': 'wat',
                         'city': 'here'}
                    ]
                 },
                 'paul@example.com'),
                ({
                    '_id': 'paul@example.com',
                    'name': 'paul',
                    'addresses':[
                        {'street': 'wat',
                         'city': 42}
                    ]
                 },
                 psycopg2.IntegrityError),
            ]
        }

        _test_constraint(self, coll, spec)
