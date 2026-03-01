# `pysled`

Python package for parsing Sled and serializing Python objects as Sled.


## Parse: Sled to Python `dict`

To parse Sled into a Python `dict`, call `from_sled()`.

```python
from pysled import from_sled

with open("path/to/my_file.sled", mode="r") as f:
    data = from_sled(f.read())
```


## Serialize: Python to Sled

This package provides 2 ways to serialize Python objects.
1. Call `to_sled()`.
2. Instantiate a `SledSerializer` and call its `to_sled()` method.

Both have the same configuration options and defaults.
For details, refer to the `SledSerializer` documentation.

Approach #1 simply does approach #2 under the hood.
Approach #2 may be useful if you want to set a configuration once
and reuse that for serialization multiple times.

```python
from pysled import SledSerializer, to_sled

data = {}
other_data = {}

# Approach #1
sled = to_sled(data)

# Approach #2
sled_serializer = SledSerializer()
sled = sled_serializer.to_sled(data)
other_sled = sled_serializer.to_sled(other_data)
```

### Default serialization

Instances of the following Python data types (on the left) will be serialized
as the associated Sled data type (on the right).
- `None`: `nil`
- `bool`: `boolean`
- `bytes`: `hex`
- `int`: `integer`
- `float`: `float`
- `str`: `identity`, `quote`, or `concat`
- `Mapping[str, Entity]`: `smap`
- `Mapping[int, Entity]`: `imap`
- `Iterable` that is not a `Mapping`: `list`
- dataclass: `smap`

For an object to be serialized as a standalone Sled document,
it should be a `Mapping[str, Entity]` or dataclass instance,
since the top level of a Sled document is always a `smap`.

A dataclass instance is implicitly converted into a `Mapping`
by calling `dataclasses.fields()` (unless the original instance is itself
also a `Mapping`, in which case that takes precedence).
