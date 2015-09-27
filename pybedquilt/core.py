import psycopg2
import json


MIN_SERVER_VERSION = '0.3.1'


def _query(cursor, query_string, params=None):
    if params is None:
        params = tuple()
    cursor.execute(query_string, params)
    result = cursor.fetchall()
    return result


class BedquiltCursor(object):
    def __init__(self, collection, query, params):
        self.collection = collection
        self.cursor = collection.client.connection.cursor()
        self.cursor.execute(query, params)

    def __iter__(self):
        return self

    def next(self):
        n = self.cursor.fetchone()
        if n:
            return _result_row_to_dict(n)
        else:
            raise StopIteration


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

        if (connection is not None
            and isinstance(connection, psycopg2._psycopg.connection)):
            self.connection = connection
        elif dsn is not None and type(dsn) in {str, unicode}:
            self.connection = psycopg2.connect(dsn)
        elif kwargs:
            self.connection = psycopg2.connect(**kwargs)
        else:
            raise Exception("Cannot create connection")

        self.connection.autocommit = True

        self._bootstrap()

        assert self.connection is not None

    def _bootstrap(self):
        """
        Do whatever needs to be done to bootstrap/initialize the client.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
        select * from pg_catalog.pg_extension
        where extname = 'bedquilt';
        """)
        result = cursor.fetchall()

        assert (result is not None and len(result) > 0), \
            "Bedquilt extension not found on database server"

        cursor.execute("""
        select bq_assert_minimum_version('{}')
        """.format(MIN_SERVER_VERSION))
        _ = cursor.fetchall()

    def create_collection(self, collection_name):
        """
        Create a collection.
        Args:
          - collection_name: string name of collection.
        Returns:
          - Boolean representing whether the collection was created or not.
        """
        result = _query(self.connection.cursor(), """
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
        result = _query(self.connection.cursor(), """
        select bq_delete_collection(%s)
        """, (collection_name,))
        return result[0][0]

    def list_collections(self):
        """
        Get a list collections on the database server.
        Args: None
        Returns: List of string names of collections.
        """
        result = _query(self.connection.cursor(), """
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
        self.cursor = client.connection.cursor()

    def _query(self, query_string, params):
        return _query(self.cursor, query_string, params)

    # Read
    def find(self, query_doc=None, skip=0, limit=None, sort=None):
        """
        Find documents in collection.
        Args:
          - query_doc: dict representing query.
          - skip: integer number of documents to skip (default 0).
          - limit: integer number of documents to limit result set to (default None).
          - sort: list of dict, representing sort specification.
        Returns: BedquiltCursor
        """
        if query_doc is None:
            query_doc = {}
        assert type(query_doc) is dict

        if sort is not None:
            assert type(sort) is list
            sort = json.dumps(sort)

        return BedquiltCursor(self, """
        select bq_find(%s, %s::json, %s, %s, %s::json);
        """, (self.collection_name, json.dumps(query_doc),
              skip, limit, sort))

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

    def count(self, query_doc=None):
        """
        Get a count of documents in this collection, with an optional
        query document to match.
        Args:
          - query_doc: dict representing query. (optional)
        Returns: Integer representing count of
        documents in collection matching query
        """
        if query_doc is None:
            query_doc = {}

        assert type(query_doc) is dict

        result = self._query("""
        select bq_count(%s, %s);
        """, (self.collection_name, json.dumps(query_doc)))

        return result[0][0]

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

    def add_constraints(self, constraint_spec):
        """
        Add constraints to this collection.
        Args:
          - constraint_spec: dict describing constraints to add
        Returns: boolean, indicating whether any of the constraint
        rules were applied.
        """
        assert type(constraint_spec) is dict
        result = self._query("""
        select bq_add_constraints(%s, %s::json);
        """, (self.collection_name, json.dumps(constraint_spec)))
        return result[0][0]

    def list_constraints(self):
        """
        List all constraints on this collection.
        Returns: list of strings.
        """
        result = self._query("""
        select bq_list_constraints(%s);
        """, (self.collection_name,))
        return map(lambda r: r[0], result)

    def remove_constraints(self, constraint_spec):
        """
        Remove constraints to this collection.
        Args:
          - constraint_spec: dict describing constraints to be removed
        Returns: boolean, indicating whether any of the constraint
        rules were removed.
        """
        assert type(constraint_spec) is dict
        result = self._query("""
        select bq_remove_constraints(%s, %s::json);
        """, (self.collection_name, json.dumps(constraint_spec)))
        return result[0][0]

# Helpers
def _result_row_to_dict(json_row):
    if len(json_row) != 1:
        raise Exception("something wrong with row: {}".format(json_row))
    return json_row[0]
