# Parsled

Python package for parsing Sled and serializing Python objects as Sled.

Sled is a serialization language for developer-friendly reading and writing.


## Setup

`parsled` is available on PyPI.
You can install it using your preferred Python package manager.
E.g.
```sh
pip install parsled
```


## Parse: Sled to Python `dict`

To parse a `str` of Sled into a Python `dict`, call `from_sled()`.

```python
sled_text = '''
name = "John Doe"
age = 50
children = [Jack ; Jill]
'''

data = parsled.from_sled(sled_text)

assert data == {
    "name": "John Doe",
    "age": 50,
    "children": ["Jack", "Jill"],
}
```

To parse a Sled file, read it to a `str`, then pass that into `from_sled()`.
```python
with open("path/to/my_file.sled", mode="r") as f:
    sled_text = f.read()
    data = parsled.from_sled(sled_text)
```


## Serialize: Python `object` to Sled

We have 2 main ways to serialize Python objects.

1. Call `to_sled()`.
2. Instantiate a `SledSerializer` and call its `to_sled()` method.

Both have the same configuration options and defaults.
For details, refer to the `SledSerializer` documentation.

Approach #1 simply does approach #2 under the hood.
Approach #2 may be useful if you want to set a configuration once
and reuse that for serialization multiple times.

```python
data = {}
other_data = {}

# Approach #1
sled_output = parsled.to_sled(data)

# Approach #2
sled_serializer = parsled.SledSerializer()
sled_output = sled_serializer.to_sled(data)
other_sled_output = sled_serializer.to_sled(other_data)
```
