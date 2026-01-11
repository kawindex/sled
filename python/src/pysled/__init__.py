"""
Python package for parsing Sled and serializing Python objects as Sled.

Sled is a serialization language for developer-friendly reading and writing.
"""

from pysled._sled_error import SledError, SledErrorCategory
from pysled._parser import from_sled
from pysled._serializer import SledSerializer, to_sled
from pysled._serializer_basic import SLED_CUSTOM_SERIALIZATION_METHOD_NAME
from pysled._serializer_mini import SledSerializerMini, to_sled_mini
