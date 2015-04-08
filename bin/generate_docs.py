#! /usr/bin/env python

import string
import inspect
import pybedquilt
import os


TARGET_FILE_PATH = 'docs/api_docs.md'
MAGIC_LINE = '---- ---- ---- ----'


def get_docs(some_class):
    result = []
    for attr_string in [x for x in dir(some_class)
                    if x == '__init__' or not x.startswith('_')]:

        class_dict = some_class.__dict__
        attr = class_dict[attr_string]
        docstring = attr.__doc__

        result.append({
            'name': attr_string,
            'docstring': docstring
        })

    return result


def main():
    # BedquiltClient
    client_docs = get_docs(pybedquilt.BedquiltClient)
    collection_docs = get_docs(pybedquilt.BedquiltCollection)

    final_string = (
"""

## BedquiltClient

{}

## BedquiltCollection

{}

""".format(
    "\n".join(map(to_md, client_docs)),
    "\n".join(map(to_md, collection_docs))
)
    )

    contents = None
    with open(TARGET_FILE_PATH, 'r') as target:
        contents = target.readlines()

    final_contents = []
    for line in contents:
        if line.strip() != MAGIC_LINE.strip():
            final_contents.append(line)
        else:
            final_contents.append(MAGIC_LINE)
            final_contents.append('\n')
            break

    for line in final_string.splitlines():
        final_contents.append(line)
        final_contents.append('\n')

    with open(TARGET_FILE_PATH, 'w') as target:
        target.writelines(final_contents)


# Helpers
def md_escape(st):
    return st.replace('_', '\_')


def to_md(doc):
    return (
"""

### {}

```
{}
```
""".format(md_escape(doc['name']), doc['docstring'])
    )


# Run if main
if __name__ == '__main__':
    main()
