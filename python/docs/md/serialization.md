# Serialization using `parsled`

## Basic usage

{{ serialization_docstring }}

## Data types

By default, instances of the following Python data types (on the left)
will be serialized to the corresponding Sled data type (on the right).

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


## Mini serialization

{{ mini_serialization_docstring }}
