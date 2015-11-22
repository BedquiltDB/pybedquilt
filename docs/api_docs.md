# API Docs

This document describes the Python classes available in the `pybedquilt` module.

---- ---- ---- ----


## BedquiltClient



### \_\_init\_\_

```

        Create a BedquiltClient object, connecting to the database server.
        Args:
          - dsn: A psycopg2-style dsn string
        Example:
          - BedquiltClient("dbname=test")
        
```



### collection

```

        Get a BedquiltCollection object.
        Args:
          - collection_name: string name of collection.
        Returns: Instance of BedquiltCollection.
        
```



### collection\_exists

```

        Check if a collection exists.
        Args:
          - collection_name: string name of collection.
        Returns: Boolean
        
```



### create\_collection

```

        Create a collection.
        Args:
          - collection_name: string name of collection.
        Returns:
          - Boolean representing whether the collection was created or not.
        
```



### delete\_collection

```

        Delete a collection.
        Args:
          - collection_name: string name of collection.
        Returns:
          - Boolean representing whether the collection was deleted or not.
        
```



### list\_collections

```

        Get a list collections on the database server.
        Args: None
        Returns: List of string names of collections.
        
```


## BedquiltCollection



### \_\_init\_\_

```

        Create a BedquiltCollection object.
        Args:
          - client: instance of BedquiltClient.
          - collection_name: string name of collection.
        
```



### add\_constraints

```

        Add constraints to this collection.
        Args:
          - constraint_spec: dict describing constraints to add
        Returns: boolean, indicating whether any of the constraint
        rules were applied.
        
```



### count

```

        Get a count of documents in this collection, with an optional
        query document to match.
        Args:
          - query_doc: dict representing query. (optional)
        Returns: Integer representing count of
        documents in collection matching query
        
```



### distinct

```

        Get a sequence of the distinct values in this collection,
        at the specified key-path.
        Args:
          - key_path: string specifying the key to look up
        Returns: BedquiltCursor
        Example: collection.distinct('address.city')
        
```



### find

```

        Find documents in collection.
        Args:
          - query_doc: dict representing query.
          - skip: integer number of documents to skip (default 0).
          - limit: integer number of documents to limit result set to (default None).
          - sort: list of dict, representing sort specification.
        Returns: BedquiltCursor
        
```



### find\_one

```

        Find a single document in collection.
        Args:
          - query_doc: dict representing query.
        Returns: A dictionary if found, or None.
        
```



### find\_one\_by\_id

```

        Find a single document in collection.
        Args:
          - doc_id: string to match against '_id' fields of collection.
        Returns: A dictionary if found, or None.
        
```



### insert

```

        Insert a dictionary into collection.
        Args:
          - doc: dict representing document to insert.
        Returns: string _id of saved document.
        
```



### list\_constraints

```

        List all constraints on this collection.
        Returns: list of strings.
        
```



### remove

```

        Remove documents from the collection.
        Args:
          - query_doc: dictionary representing the query to match documents to remove.
        Returns: integer number of documents removed.
        
```



### remove\_constraints

```

        Remove constraints to this collection.
        Args:
          - constraint_spec: dict describing constraints to be removed
        Returns: boolean, indicating whether any of the constraint
        rules were removed.
        
```



### remove\_one

```

        Remove a single document from the collection.
        The first document to match the query doc will be removed.
        Args:
          - query_doc: dictionary representing the query to match documents to remove.
        Returns: integer number of documents removed.
        
```



### remove\_one\_by\_id

```

        Remove a single document from the collection.
        Args:
          - doc_id: string _id of the document to remove.
        Returns: integer number of documents removed.
        
```



### save

```

        Save a dict to collection. If the doc has an '_id' field and there is a
        document in the collection with that _id, then that document will be
        over-written by the supplied document. Otherwise, this behaves like insert.
        Args:
          - doc: python dict representing doc to save.
        Returns: string _id field of saved document.
        
```


