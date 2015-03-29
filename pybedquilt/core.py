import psycopg2
import json


class BedquiltClient(object):

    def __init__(self, dsn=None):
        self.connection = None
        self.cursor = None
        if dsn is not None:
            self.connection = psycopg2.connect(dsn)
            self.cursor = self.connection.cursor()
        else:
            raise Exception("Cannot create connection")

    def collection(self, collection_name):
        return BedquiltCollection(self, collection_name)

    def __getitem__(self, collection_name):
        return self.collection(collection_name)


class BedquiltCollection(object):

    def __init__(self, client, collection_name):
        self.client = client
        self.collection_name = collection_name

    def _query(self, query_string):
        self.client.cursor.execute(query_string)
        result = self.client.cursor.fetchall()
        return result

    def find(self, query_doc=None):
        if query_doc is None:
            query_doc = {}

        result = self._query("""
        select bq_find('{}', '{}')
        """.format(self.collection_name, json.dumps(query_doc)))

        return map(_result_row_to_dict, result)


# Helpers
def _result_row_to_dict(json_row):
    if len(json_row) != 1:
        raise Exception("something wrong with row: {}".format(json_row))
    return json_row[0]
