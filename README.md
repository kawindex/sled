# Sled

A format for representing data that developers will directly interact with, like config files.
(Though with language models, who knows if humans will be doing this for much longer?)

Sled is intended to be simple and convenient for a human (and maybe AI-augmented) developer to both read and write.

See [`pysled`](/python) for a simple parser and serializer.


## Sled by example

```sled
# This is a comment

my_string = "use quotes if you have spaces or other special cases"
"another_string" = otherwise_quotes_are_optional

my_integer = 123
my_float = 4.5

# Keywords are denoted by `@`
boolean_true = @true
boolean_false = @false
distinguished_nil = @nil

my_list = [
  # The elements of a list can be anything
  "Lorem ipsum"
  3.14
  @false
]

"This is a smap. Each key is a string. (The root level is itself a smap.)" = {
  something = xyz          # The key must be a string
  "another thing" = @true  # The value can be anything
}

"This is an imap. Each key is an integer." = {
  3 = @nil     # Again, the value can be anything
  -100 = 4.0   # Even an integer or float
}

# If you want multiple entries of a list, smap, or imap on the same line,
# they must be separated by `;`
colors = [
  orange ; red
  green
  yellow ; purple ; brown
  blue ; pink
]

# You can arbitrarily nest any list, smap, and imap within one another
grocery_store = [
  {
    name = avocado
    in_stock = @true
    price = 1.29
    buyers = [ Alice ; Bob ]
  }
  { name = banana ; in_stock = @true ; price = 0.15 ; buyers = [] }
  { name = coconut ; in_stock = @false ; price = 2.97 ; buyers = [] }
]

"Supports most of Unicode?" = {
  English = Yes!
  español = ¡Sí!
  中文 = 是的！
  emoji = ✅🎉
}
```
