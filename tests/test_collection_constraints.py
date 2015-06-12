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
        with self.assertRaises(psycopg2.IntegrityError):
            coll.insert({
                '_id': 'paul@example.com',
                'age': 20
            })
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
