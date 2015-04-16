import psycopg2
import json


def _query(client, query_string, params=None):
    if params is None:
        params = tuple()
    client.cursor.execute(query_string, params)
    result = client.cursor.fetchall()
    return result


class BedquiltClient(object):

    def __init__(self, dsn=None, connection=None, spec=None, **kwargs):
        """
        Create a BedquiltClient object, connecting to the database server.
        Args:
          - dsn: A psycopg2-style dsn string
        Example:
          - BedquiltClient("dbname=test")
        """
        self.connection = None
        self.cursor = None

        if connection is not None and isinstance(connection, psycopg2._psycopg.connection):
            self.connection = connection
            self.cursor = self.connection.cursor()
        elif dsn is not None and type(dsn) in {str, unicode}:
            self.connection = psycopg2.connect(dsn)
            self.connection.autocommit = True
            self.cursor = self.connection.cursor()
        elif kwargs:
            self.connection = psycopg2.connect(**kwargs)
            self.connection.autocommit = True
            self.cursor = self.connection.cursor()
        else:
            raise Exception("Cannot create connection")

        self._bootstrap()

        assert self.connection is not None
        assert self.cursor is not None

    def _bootstrap(self):
        """
        Do whatever needs to be done to bootstrap/initialize the client.
        """
        self.cursor.execute("""
        select * from pg_catalog.pg_extension
        where extname = 'bedquilt';
        """)
        result = self.cursor.fetchall()
        assert (result is not None and len(result) > 0), \
            "Bedquilt extension not found on database server"

    def create_collection(self, collection_name):
        """
        Create a collection.
        Args:
          - collection_name: string name of collection.
        Returns:
          - Boolean representing whether the collection was created or not.
        """
        result = _query(self, """
        select bq_create_collection(%s)
        """, (collection_name,))
        return result[0][0]

    def delete_collection(self, collection_name):
        """
        Delete a collection.
        Args:
          - collection_name: string name of collection.
        Returns:
          - Boolean representing whether the collection was deleted or not.
        """
        result = _query(self, """
        select bq_delete_collection(%s)
        """, (collection_name,))
        return result[0][0]

    def list_collections(self):
        """
        Get a list collections on the database server.
        Args: None
        Returns: List of string names of collections.
        """
        result = _query(self, """
        select bq_list_collections();
        """)

        return map(lambda r: r[0], result)

    def collection(self, collection_name):
        """
        Get a BedquiltCollection object.
        Args:
          - collection_name: string name of collection.
        Returns: Instance of BedquiltCollection.
        """
        return BedquiltCollection(self, collection_name)

    def __getitem__(self, collection_name):
        return self.collection(collection_name)


class BedquiltCollection(object):

    def __init__(self, client, collection_name):
        """
        Create a BedquiltCollection object.
        Args:
          - client: instance of BedquiltClient.
          - collection_name: string name of collection.
        """
        self.client = client
        self.collection_name = collection_name

    def _query(self, query_string, params):
        return _query(self.client, query_string, params)

    # Read
    def find(self, query_doc=None):
        """
        Find documents in collection.
        Args:
          - query_doc: dict representing query.
        Returns: List of dictionaries.
        """
        if query_doc is None:
            query_doc = {}
        assert type(query_doc) is dict

        result = self._query("""
        select bq_find(%s, %s::json);
        """, (self.collection_name, json.dumps(query_doc)))

        return map(_result_row_to_dict, result)

    def find_one(self, query_doc=None):
        """
        Find a single document in collection.
        Args:
          - query_doc: dict representing query.
        Returns: A dictionary if found, or None.
        """
        if query_doc is None:
            query_doc = {}
        assert type(query_doc) is dict

        result = self._query("""
        select bq_find_one(%s, %s::json);
        """, (self.collection_name, json.dumps(query_doc)))

        if len(result) == 1:
            return _result_row_to_dict(result[0])
        else:
            return None

    def find_one_by_id(self, doc_id):
        """
        Find a single document in collection.
        Args:
          - doc_id: string to match against '_id' fields of collection.
        Returns: A dictionary if found, or None.
        """

        assert type(doc_id) in {str, unicode}

        result = self._query("""
        select bq_find_one_by_id(%s, %s);
        """, (self.collection_name, doc_id))

        if len(result) == 1:
            return _result_row_to_dict(result[0])
        else:
            return None

    # Create
    def insert(self, doc):
        """
        Insert a dictionary into collection.
        Args:
          - doc: dict representing document to insert.
        Returns: string _id of saved document.
        """
        assert type(doc) is dict
        result = self._query("""
        select bq_insert(%s, %s::json);
        """, (self.collection_name, json.dumps(doc)))
        return result[0][0]

    # Update
    def save(self, doc):
        """
        Save a dict to collection. If the doc has an '_id' field and there is a
        document in the collection with that _id, then that document will be
        over-written by the supplied document. Otherwise, this behaves like insert.
        Args:
          - doc: python dict representing doc to save.
        Returns: string _id field of saved document.
        """
        assert type(doc) is dict
        result = self._query("""
        select bq_save(%s, %s::json);
        """, (self.collection_name, json.dumps(doc)))
        return result[0][0]

    # Delete
    def remove(self, query_doc):
        """
        Remove documents from the collection.
        Args:
          - query_doc: dictionary representing the query to match documents to remove.
        Returns: integer number of documents removed.
        """
        assert type(query_doc) is dict
        result = self._query("""
        select bq_remove(%s, %s::json);
        """, (self.collection_name, json.dumps(query_doc)))
        return result[0][0]

    def remove_one(self, query_doc):
        """
        Remove a single document from the collection.
        The first document to match the query doc will be removed.
        Args:
          - query_doc: dictionary representing the query to match documents to remove.
        Returns: integer number of documents removed.
        """
        assert type(query_doc) is dict
        result = self._query("""
        select bq_remove_one(%s, %s::json);
        """, (self.collection_name, json.dumps(query_doc)))
        return result[0][0]

    def remove_one_by_id(self, doc_id):
        """
        Remove a single document from the collection.
        Args:
          - doc_id: string _id of the document to remove.
        Returns: integer number of documents removed.
        """
        assert type(doc_id) in {str, unicode}
        result = self._query("""
        select bq_remove_one_by_id(%s, %s);
        """, (self.collection_name, doc_id))
        return result[0][0]


# Helpers
def _result_row_to_dict(json_row):
    if len(json_row) != 1:
        raise Exception("something wrong with row: {}".format(json_row))
    return json_row[0]
