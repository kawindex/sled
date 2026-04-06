"""
Python package for parsing Sled and serializing Python objects as Sled.

Sled is a serialization language for developer-friendly reading and writing.
"""


import parsled._check_sys_float_range as _

from parsled._sled_error import SledError, SledErrorCategory
from parsled._parser import from_sled
from parsled._serializer import SledSerializer, to_sled
from parsled._serializer_basic import SLED_CUSTOM_SERIALIZATION_METHOD_NAME
from parsled._serializer_mini import SledSerializerMini, to_sled_mini
from parsled.spec import Entity
