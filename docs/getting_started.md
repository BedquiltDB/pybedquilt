# Getting Started

First, install the [BedquiltDB](http://bedquiltdb.github.io) extension on your
PostgreSQL instance, then create enable the extension on a database:
```
-- in psql
CREATE DATABASE bedquilt_test;

-- connect to bedquilt_test and then run:
CREATE EXTENSION pgcrypto;
CREATE EXTENSION bedquilt;
```

Then, install the pybedquilt libary:
```
$ pip install pybedquilt
```


## Inserting Data

Now, let's open a python interpreter and create a `BedquiltClient`:
```
$ python
>>> import pybedquilt
>>> client = pybedquilt.BedquiltClient("dbname=bedquilt_test")
```

Once we have a client, connected to the PostgreSQL server, we can get
a `BedquiltCollection` object:
```
>>> people = client['people']
```

Lets put some people documents in our collection:
```
>>> sarah = {
...    '_id': "sarah@example.com",
...    'name': "Sarah Jones",
...    'age': 27,
...    'city': "Edinburgh",
...    'likes': ["icecream", "code", "tigers"]
... }
>>> dave = {
...    'name': "Dave",
...    'age': 40,
...    'city': "London",
...    'likes': ["code", "puppies", "knitting"]
... }
>>> elaine = {
...    'name': "Elaine",
...    'age': 36,
...    'city': "Edinburgh",
...    'likes': ["board games", "cider", "owls"]
... }
>>> people.insert(sarah)
'sarah@example.com'
>>> people.insert(dave)
'99a5cb8648566901436e2967'
>>> people.insert(elaine)
'cabb5c9f6a55ecdebbc42c69'
```

As you can see, we can insert any python dictionary which can be serialized to JSON.
When we insert a document (or dict, if you prefer), the `insert` method returns the
`_id` field of the document. If the document does not have an `_id` key already,
a random one will be generated on the server. The `_id` field must be unique for
all documents in the collection.


## Finding Data

With a few (well, two) documents in our `people` collection, we can then query the
collection and see what comes back:
```
>>> people.find({'city': "Edinburgh"})
[{'_id': 'sarah@example.com', ....}, {'_id': 'cabb5c9f6a55ecdebbc42c69', ...}]
```

In this case we get a list of two documents back, corresponding to the two
people who live in Edinburgh, `sarah` and `elaine`.

The first (and only) argument to the `find` method is a query dictionary. A document
matches the query if its contents are a superset of the query data. In our example,
we're basically saying `"find documents where the city field is 'Edinburgh"`.

We can also query on the contents of nested JSON data structures, for example if
we wanted to get all documents where the person likes "code":
```
>>> people.find({'likes': ['code']})
[ {...}, {...} ]
```

That query returns the two documents for `sarah` and `dave`.

We can also limit the result set to a single document matching our query by using
`find_one` method:
```
>>> people.find_one({'likes': ['code']})
{'_id': 'sarah@example.com' ...}
```

If we know the `_id` key of a document we want, we can query for that document
directly, using `find_one_by_id`:
```
>>> people.find_one_by_id('sarah@example.com')
{'_id': 'sarah@example.com', 'name': 'Sarah Jones'...}
```

## Updating Existing Documents

We modify and save an existing document too, using the `save` method:
```
doc = people.find_one_by_id('sarah@example.com')
doc['job'] = "Web Developer"
doc['likes'].append("Javascript")
people.save(doc)
```

If the saved document has an `_id` which matches a document in the collection,
it will be overwritten with the new data. If not, then `save` behaves just like the
`insert` method.


## Removing Documents

We can delete data from a collection using the `remove`, `remove_one`
and `remove_one_by_id` methods. They work exactly as you'd expect:
```
people.remove({'cool': False})
people.remove_one({'likes': ['cabbage']})
people.remove_one_by_id('magic_man@example.com')
```
