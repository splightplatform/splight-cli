# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: logs.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from google.protobuf import (
    timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2,
)

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\nlogs.proto\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1bgoogle/protobuf/empty.proto"`\n\x08LogEntry\x12-\n\ttimestamp\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x14\n\x0c\x63omponent_id\x18\x02 \x01(\t\x12\x0f\n\x07message\x18\x03 \x01(\t2G\n\x0bLogsService\x12\x38\n\x0fstash_log_entry\x12\t.LogEntry\x1a\x16.google.protobuf.Empty"\x00(\x01\x62\x06proto3'
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "logs_pb2", globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _LOGENTRY._serialized_start = 76
    _LOGENTRY._serialized_end = 172
    _LOGSSERVICE._serialized_start = 174
    _LOGSSERVICE._serialized_end = 245
# @@protoc_insertion_point(module_scope)
