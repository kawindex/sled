# Sled specification

[Grammar](/sled/grammar.md)

## Types

`concrete` types:
- `nil` (only `@nil`)
- `boolean` (only `@true` and `@false`)
- `integer` (int64)
- `float` (includes `@inf`, `@ninf` and `@nan`)
- `hex` (binary data)
- `string` (3 representations)
  - `identity`
  - `quote`
  - `concat`

`container` types:
- `smap`
- `imap`
- `list`


## Top level Sled document

The top-level Sled document must be a `smap`,
but enclosing braces can be omitted.

Enclosing braces can be used to indicate the start and end
of the Sled document.


## `container` order

- Within each `smap` and each `imap`, key-value pairs are unordered relative to one another.
- Within each `list`, the entities are in the given order.


## `nil` evaluation

`@nil` is intended to be a distinguished representation of a null value.

In particular, for a precise parser implementation, `@nil` must always evaluate to
the same value, ideally a singleton, that is distinct from the evaluation of
each of the following.
- `@true`
- `@false`
- `0` (`integer` zero)
- `0.0` (`float` zero)
- `@hex()` (empty `hex`)
- `""` (empty `string`)
- `{}` (empty `map`)
- `[]` (empty `list`)


## `boolean` evaluation

For a precise parser implementation, all of the following must apply.
- `@true` must always evaluate to the same true boolean value.
- `@false` must always evaluate to the same false boolean value.
- Both of these should be distinguished boolean values
- These should be the only 2 possible boolean values.


## `integer` evaluation

Underscores, leading zeros and the positive sign (`+`) are all ignored.
The result of evaluating `-0` is the same as that of evaluating `0`.

Each `integer` evaluates to a (signed) integer that can be represented
using two's complement notation with 64 bits.

The minimum `integer` is `-(2^63)`, which is `-9223372036854775808`.
The maximum `integer` is `2^63 - 1`, which is `9223372036854775807`.

A precise parser implementation must support exactly (only) this range
and must error on both positive and negative overflow.


## `float` evaluation

The evaluation of a `float` is approximate and may vary across
different parsers and hardware. As a result, `float` evaluation
has weaker guarantees than that for other types.

At the very least, `float` evaluation should be reasonable and intuitive.
A precise parser implementation must treat each `float` as
a 64-bit floating point number that adheres to the IEEE-754 standard.

- `@inf` evaluates to a value that is positive and infinite.
- `@ninf` evaluates to a value that is negative and infinite.
- `@nan` evaluates to a value that represents a NaN ("not a number").
- Every other Sled `float` evaluates to a finite non-NaN value.

A precise parser implementation must error on both overflow and underflow.


## `hex` evaluation

Each `hex` evaluates to a representation of some bytes or binary data.

Underscores and `ws` are ignored.


## `string` evaluation

All `string` representations evaluate to sequences of Unicode codepoints.
They must all evaluate to the same type.

### `quote` escape sequences

A `quote` uses the backslash (`\`) as its escape character.
It may contain the following escape sequences, which are evaluated as follows.
- `\\`: backslash (`\`)
- `\"`: double quote (`"`)
- `\'`: single quote (`'`)
- `\n`: line feed
- `\r`: carriage return
- `\t`: tabulation (tab)
- `\u{X}`: Unicode code point (`X` contains only hexadecimal digits or underscores, including at least 1 hexadecimal digit)

### `concat` evaluation

Each `concat` is composed of segments, each of which is a `quote`.

The evaluation of a `concat` is the concatenation obtained by
evaluating each of its segments and concatenating the results as-is,
without any delimiter.


## Key equivalence

Within each `smap` and each `imap`, each key must be distinct
from every other key. No two keys can be equivalent, even if they map to
equivalent values (i.e. repeated key-value pairs are disallowed).

Keys are equivalent iff they have the same integer/string evaluation.

### `string` keys in `smap`

`identity`, `quote` and `concat` are just different representations of
a `string`. Different `string` representations are equivalent iff
they evaluate to the same string (even if they differ in, for instance,
how some characters are escaped).

### `integer` keys in `imap`

- Underscores, leading zeros and the positive sign (`+`) are all ignored.
- All `integer` representations of zero (`+0`, `-0`, `0`, etc.) are equivalent.


## More readable form for `identity_symbol` and `identity_start_symbol`

`identity_symbol` and `identity_start_symbol` are more intuitively understood
in terms of the values they _cannot_ take, which is unfortunately
rather cumbersome in the [formal grammar](/sled/grammar.md).
Each definition is reproduced here in a more readable form.

`identity_symbol` can (only) be any Unicode code point up to `10FFFF`, except for the following:
- the 32 C0 control characters, along with `DEL` (this includes the tab and line separators)
- the space
- parentheses, square brackets, curly braces, angled brackets (`()[]{}<>`)
- equal (`=`), semicolon (`;`)
- single quote (`'`), double quote (`"`)
- backslash
- comment mark (`#`)

`identity_start_symbol` can (only) be any `identity_symbol`, except for the following:
- any digit (0-9)
- underscore (`_`)
- positive sign (`+`), negative sign (`-`)
- period (`.`), comma (`,`)
- keyword mark (`@`)
