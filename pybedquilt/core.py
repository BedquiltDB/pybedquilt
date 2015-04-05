import psycopg2
import json


def _query(client, query_string):
    client.cursor.execute(query_string)
    client.connection.commit()
    result = self.client.cursor.fetchall()
    return result


class BedquiltClient(object):

    def __init__(self, dsn=None):
        self.connection = None
        self.cursor = None
        if dsn is not None:
            self.connection = psycopg2.connect(dsn)
            self.cursor = self.connection.cursor()
        else:
            raise Exception("Cannot create connection")

        self._bootstrap()

        assert self.connection is not None
        assert self.cursor is not None

    def _bootstrap(self):
        self.cursor.execute("""
        select * from pg_catalog.pg_extension
        where extname = 'bedquilt';
        """)
        result = self.cursor.fetchall()
        assert (result is not None and len(result) > 0), \
            "Bedquilt extension not found on database server"

    def create_collection(self, collection_name):
        result = _query(self, """
        select bq_create_collection('{}')
        """.format(collection_name))
        return result[0][0]

    def delete_collection(self, collection_name):
        result = _query(self, """
        select bq_delete_collection('{}')
        """.format(collection_name))
        return result[0][0]

    def collection(self, collection_name):
        return BedquiltCollection(self, collection_name)

    def __getitem__(self, collection_name):
        return self.collection(collection_name)


class BedquiltCollection(object):

    def __init__(self, client, collection_name):
        self.client = client
        self.collection_name = collection_name

    def _query(self, query_string):
        return _query(self.client, query_string)

    def find(self, query_doc=None):
        if query_doc is None:
            query_doc = {}
        assert type(query_doc) is dict

        result = self._query("""
        select bq_find('{}', '{}');
        """.format(self.collection_name, json.dumps(query_doc)))

        return map(_result_row_to_dict, result)

    def insert(self, doc):
        assert type(doc) is dict
        result = self._query("""
        select bq_insert('{}', '{}');
        """.format(self.collection_name, json.dumps(doc)))
        return result[0][0]

# Helpers
def _result_row_to_dict(json_row):
    if len(json_row) != 1:
        raise Exception("something wrong with row: {}".format(json_row))
    return json_row[0]
