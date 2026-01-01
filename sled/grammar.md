```
sled
    optional_ws_or_delimiters smap_content
    optional_ws smap optional_ws

entity
    smap
    imap
    list
    concrete

list
    '[' optional_ws_or_delimiters optional_entities ']'

smap
    '{' optional_ws_or_delimiters smap_content '}'

smap_content
    ""
    smap_pair optional_ws
    smap_pair optional_ws delimiter optional_ws_or_delimiters smap_content

smap_pair
    string optional_ws '=' optional_ws entity

imap
    '{' optional_ws_or_delimiters imap_content '}'

imap_content
    ""
    imap_pair optional_ws
    imap_pair optional_ws delimiter optional_ws_or_delimiters imap_content

imap_pair
    integer optional_ws '=' optional_ws entity

optional_entities
    ""
    entity optional_ws
    entity optional_ws delimiter optional_ws_or_delimiters optional_entities

optional_ws_or_delimiters
    ""
    optional_ws optional_ws_or_delimiters
    delimiter optional_ws_or_delimiters

delimiter
    ';'
    inclusive_line_separator

optional_ws
    ""
    horizontal_space optional_ws
    inclusive_line_separator optional_ws

inclusive_line_separator
    line_separator
    '#' comment line_separator

comment
    ""
    comment_symbol comment

comment_symbol
    '0009'
    '0020' . '10FFFF' - '007F'

line_separator
    '000A'
    '000D'
    '000D' '000A'

optional_horizontal_spaces
    ""
    horizontal_space optional_horizontal_spaces

horizontal_space
    '0020'
    '0009'

concrete
    string
    integer
    float
    "@hex" optional_ws '(' hex_content ')'
    "@true"
    "@false"
    "@nil"

string
    identity_string
    quote_string
    "@concat" optional_ws '(' optional_quote_strings ')'

optional_quote_strings
    ""
    quote_string optional_ws
    quote_string optional_ws delimiter optional_ws_or_delimiters optional_quote_strings

quote_string
    '"' optional_doubly_quoted_symbols '"'
    ''' optional_singly_quoted_symbols '''

optional_doubly_quoted_symbols
    ""
    doubly_quoted_symbol optional_doubly_quoted_symbols

doubly_quoted_symbol
    quoted_symbol
    '''

optional_singly_quoted_symbol
    ""
    singly_quoted_symbol optional_singly_quoted_symbol

singly_quoted_symbol
    quoted_symbol
    '"'

quoted_symbol
    '0021' . '10FFFF' - '007F' - '"' - ''' - '\'
    '0009'
    '\' '"'
    "\'"
    "\`"
    "\n"
    "\r"
    "\t"
    "\u" '{' hex_digits '}'
    "\\"

unicode_hex
    ""
    '_' unicode_hex
    hex_digit unicode_hex

identity_string
    identity_start_symbol optional_bare_symbols

optional_bare_symbols
    ""
    identity_symbol optional_bare_symbols

identity_symbol
    identity_start_symbol
    '0' . '9'
    '_'
    '-'
    '+'
    '.'
    ','
    '@'

identity_start_symbol
    '0021' . '10FFFF' - '007F' - ' ' - '0' . '9' - '_' - '-' - '+' - '.' - ',' - '@' - '#' - '=' - ';' - '[' - ']' - '{' - '}' - '(' - ')' - '<' - '>' - '"' - ''' - '\'

float
    "@nan"
    "@inf"
    "@ninf"
    integer decimal_mark optional_digits optional_exponent
    integer exponent
    optional_sign optional_digits decimal_mark one_or_more_digits optional_exponent

integer
    optional_sign one_or_more_digits

decimal_mark
    '.'
    ','

hex_content
    ""
    optional_hex_separators hex_content
    hex_digit optional_hex_separators hex_digit hex_content

hex_digit
    digit
    'A' . 'F'
    'a' . 'f'

optional_hex_separators
    ""
    optional_ws optional_hex_separators
    '_' optional_hex_separators

optional_exponent
    ""
    exponent

exponent
    exponent_marker integer

exponent_marker
    'E'
    'e'

one_or_more_digits
    optional_digit_separators digit optional_digits

optional_digits
    ""
    digit digits
    '_' digits

optional_digit_separators
    ""
    '_' optional_digit_separators

digit
    '0' . '9'

optional_sign
    ""
    sign
    '_' optional_sign

sign
    '-'
    '+'
```
