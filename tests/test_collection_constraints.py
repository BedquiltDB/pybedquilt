import testutils
import json
import string
import psycopg2


class TestAddRequiredConstraint(testutils.BedquiltTestCase):

    def test_add_simple_required_constraint(self):
        client = self._get_test_client()
        coll = client['people']

        # add the constraint
        result = coll.add_constraints({
            'name': {'$required': 1}
        })
        self.assertEqual(result, True)

        # add the constraint again should return false
        result = coll.add_constraints({
            'name': {'$required': 1}
        })
        self.assertEqual(result, False)

        # reject bad doc
        self._test_save(
            coll,
            {'_id': 'paul@example.com',
             'age': 20},
            psycopg2.IntegrityError
        )
        self.conn.rollback()

        # accept doc with name present and null
        self.assertEquals(
            coll.save({
                '_id': 'paul@example.com',
                'name': None,
                'age': 20
            }),
            'paul@example.com'
        )

        # accept doc with name present and set to a string value
        self.assertEquals(
            coll.save({
                '_id': 'paul@example.com',
                'name': 'Paul',
                'age': 20
            }),
            'paul@example.com'
        )

    def test_required_at_nested_path(self):
        client = self._get_test_client()
        coll = client['people']

        result = coll.add_constraints({
            'address.city': {'$required': 1}
        })
        self.assertEquals(True, result)

        # reject doc without nested structure
        self._test_save(
            coll,
            {'_id': 'paul@example.com',
             'age': 20},
            psycopg2.IntegrityError
        )
        self.conn.rollback()

        # reject doc where address.city is not set
        self._test_save(
            coll,
            {'_id': 'paul@example.com',
             'age': 20,
             'address': {
                 'street': 'wat'
             }},
            psycopg2.IntegrityError
        )
        self.conn.rollback()

        # accept doc with address.city present and null
        self.assertEquals(
            coll.save({
                '_id': 'paul@example.com',
                'name': None,
                'age': 20,
                'address': {
                    'street': 'wat',
                    'city': None
                }
            }),
            'paul@example.com'
        )

        # accept doc with name present and set to a string value
        self.assertEquals(
            coll.save({
                '_id': 'paul@example.com',
                'name': 'Paul',
                'age': 20,
                'address': {
                    'street': 'wat',
                    'city': 'London'
                }
            }),
            'paul@example.com'
        )

    def test_required_at_nested_array_path(self):
        client = self._get_test_client()
        coll = client['people']

        result = coll.add_constraints({
            'addresses.0.city': {'$required': 1}
        })
        self.assertEquals(True, result)

        # reject doc without nested structure
        self._test_save(
            coll,
            {'_id': 'paul@example.com',
             'age': 20},
            psycopg2.IntegrityError
        )
        self.conn.rollback()

        # reject doc where addresses is empty
        self._test_save(
            coll,
            {'_id': 'paul@example.com',
             'age': 20,
             'addresses': []},
            psycopg2.IntegrityError
        )
        self.conn.rollback()

        # reject doc where addresses.0.city is not set
        self._test_save(
            coll,
            {'_id': 'paul@example.com',
             'age': 20,
             'addresses': [
                 {'street': 'wat'}
             ]},
            psycopg2.IntegrityError
        )
        self.conn.rollback()

        # accept doc with address.city present and null
        self.assertEquals(
            coll.save({
                '_id': 'paul@example.com',
                'name': None,
                'age': 20,
                'addresses': [
                    {'street': 'wat',
                     'city': None}
                ]
            }),
            'paul@example.com'
        )

        # accept doc with name present and set to a string value
        self.assertEquals(
            coll.save({
                '_id': 'paul@example.com',
                'name': 'Paul',
                'age': 20,
                'addresses': [
                    {'street': 'wat',
                     'city': 'London'}
                ]
            }),
            'paul@example.com'
        )


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
