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



### count

```

        Get a count of documents in this collection, with an optional
        query document to match.
        Args:
          - query_doc: dict representing query. (optional)
        Returns: Integer representing count of
        documents in collection matching query
        
```



### find

```

        Find documents in collection.
        Args:
          - query_doc: dict representing query.
        Returns: List of dictionaries.
        
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



### remove

```

        Remove documents from the collection.
        Args:
          - query_doc: dictionary representing the query to match documents to remove.
        Returns: integer number of documents removed.
        
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


