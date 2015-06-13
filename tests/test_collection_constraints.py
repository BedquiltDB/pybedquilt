import testutils
import json
import string
import psycopg2


def _test_constraint(test, coll, spec):
    result = coll.add_constraints(spec['constraints'])
    test.assertEqual(result, True)

    result = coll.add_constraints(spec['constraints'])
    test.assertEqual(result, False)

    for data, expected_result in spec['docs']:
        test._test_save(coll, data, expected_result)


class TestAddRequiredConstraint(testutils.BedquiltTestCase):

    def test_add_simple_required_constraint(self):
        client = self._get_test_client()
        coll = client['people']

        spec = {
            'constraints': {'name': {'$required': 1}},
            'docs': [
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
            'docs': [
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
            'docs': [
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

        # add the constraint
        result = coll.add_constraints({
            'name': {'$required': 1}
        })
        self.assertEqual(result, True)

        # reject bad doc
        self._test_save(
            coll,
            {'_id': 'paul@example.com',
             'age': 20},
            psycopg2.IntegrityError
        )
        self.conn.rollback()

        # accept doc with name present and set to a string value
        self._test_save(
            coll,
            {'_id': 'paul@example.com',
             'name': 'Paul',
             'age': 20},
            'paul@example.com'
        )

        # clear the collection
        coll.remove({})

        # remove constraints
        coll.remove_constraints({
            'name': {'$required': 1}
        })

        # accept previously rejected doc
        self._test_save(
            coll,
            {'_id': 'paul@example.com',
             'age': 20},
            'paul@example.com'
        )

        # accept doc with name present and set to a string value
        self._test_save(
            coll,
            {'_id': 'paul@example.com',
             'name': 'Paul',
             'age': 20},
            'paul@example.com'
        )


class TestNotNullConstraint(testutils.BedquiltTestCase):

    def test_simple_notnull_constraint(self):
        client = self._get_test_client()
        coll = client['people']

        result = coll.add_constraints({
            'name': {'$notnull': 1}
        })
        self.assertEqual(True, result)

        # reject doc where name is set to null
        self._test_save(
            coll,
            {'_id': 'paul@example.com',
             'name': None},
            psycopg2.IntegrityError
        )

        # accept doc where name is set to string
        self._test_save(
            coll,
            {'_id': 'paul@example.com',
             'name': 'paul'},
            'paul@example.com'
        )
        coll.remove({})

        # accept doc where name is not set
        self._test_save(
            coll,
            {'_id': 'paul@example.com',
             'age': 20},
            'paul@example.com'
        )
