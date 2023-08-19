"""
support script to convert google fhir object to schema yaml
note that this has google-fhir==0.7.3 dependency, which only works with python<=3.9
"""

import sys
import json
import yaml
from proto.google.fhir.proto.stu3 import resources_pb2 as stu3, datatypes_pb2 as fhir_type, codes_pb2 as stu3_code
from google.protobuf import descriptor, json_format

# https://protobuf.dev/reference/cpp/api-docs/google.protobuf.descriptor/
PROTO_TYPE_TO_DATATYPE = {
    'TYPE_DOUBLE': 'double',
    'TYPE_FLOAT': 'float',
    'TYPE_INT64': 'integer',
    'TYPE_UINT64': 'integer',
    'TYPE_INT32': 'integer',
    'TYPE_FIXED64': 'integer',
    'TYPE_FIXED32': 'integer',
    'TYPE_BOOL': 'boolean',
    'TYPE_STRING': 'string',
    'TYPE_GROUP': 'object',
    'TYPE_MESSAGE': 'object',
    'TYPE_BYTES': 'string', # This will be changed to bytes when the type is supported
    'TYPE_UINT32': 'integer',
    'TYPE_ENUM': 'integer', # This will be changed to enum when the type is supported
    'TYPE_SFIXED32': 'integer',
    'TYPE_SFIXED64': 'integer',
    'TYPE_SINT32': 'integer',
    'TYPE_SINT64': 'integer',
}

# Currently using this to prevent hitting recursion limit due to some weird self-reference in protobuf
FHIR_TYPES = {
    # datatypes.proto https://github.com/google/fhir/blob/master/proto/google/fhir/proto/stu3/datatypes.proto
    'Reference': 'json',
    # resources.proto https://github.com/google/fhir/blob/master/proto/google/fhir/proto/stu3/resources.proto
    'ContainedResource': 'json',
    'Answer': 'json',
}


def type_helper():
    type_iterator = filter(lambda x: x.startswith('TYPE_'), descriptor.FieldDescriptor.__dict__.keys())
    type_mapping = {getattr(descriptor.FieldDescriptor, attr): PROTO_TYPE_TO_DATATYPE[attr] for attr in type_iterator}
    assert len(type_mapping) == descriptor.FieldDescriptor.MAX_TYPE
    return type_mapping

TYPE_MAPPING = type_helper()

def type_inspector(field):
    if field.message_type is not None and field.message_type.name in FHIR_TYPES:
        return FHIR_TYPES[field.message_type.name]
    elif field.message_type is not None: # nested type
        subfield = {}
        for sub in field.message_type.fields:
            if sub.name == 'extension':
                # skip extension for now
                continue
            if sub.message_type is not None and field.message_type.name == sub.message_type.name:
                # prevent protobuf infinite recursion when the message type is defined within existing message
                continue
            if sub.label == sub.LABEL_REPEATED:
                subfield[f'[{sub.name}]'] = type_inspector(sub)
            else:
                subfield[sub.name] = type_inspector(sub)
        return subfield
    else:
        return TYPE_MAPPING[field.type]

def proto_schema(obj):
    if hasattr(obj, 'DESCRIPTOR'):
        message = obj.DESCRIPTOR
    else:
        message = obj
    schema = {}
    nested = {m.name: m for m in message.nested_types}
    for field in message.fields:
        if field.name == 'extension':
            # skip extension for now
            continue
        if field.label == field.LABEL_REPEATED:
            schema[f'[{field.name}]'] = type_inspector(field)
        else:
            schema[field.name] = type_inspector(field)
    return schema

def proto_to_dict(message):
    return json_format.MessageToDict(message, including_default_value_fields=True)

def to_fixture_schema(schema):
    properties = {}
    for key, value in schema.items():
        repeat = False
        if key.startswith('[') and key.endswith(']'):
            key = key.strip('[]')
            repeat = True
        if value in PROTO_TYPE_TO_DATATYPE.values():
            if value in ('integer',):
                if repeat:
                    value = f'[{value}]'
                properties[key] = {'type': value, 'metadata': {'min': 0, 'max': 100}}
            else:
                if repeat:
                    value = f'[{value}]'
                properties[key] = {'type': value, 'metadata': {}}
        elif value == 'json':
            # Since terminal json type needs to be configured customly, replacing it with text for now
            #properties[key] = {'type': 'json', 'metadata': {}, 'properties': {}}
            properties[key] = {'type': 'text', 'metadata': {}, 'properties': {}}
        else:
            if repeat:
                properties[key] = {'type': '[json]', 'metadata': {}, 'properties': to_fixture_schema(value)}
            else:
                properties[key] = {'type': 'json', 'metadata': {}, 'properties': to_fixture_schema(value)}
    return properties

def main(*objects, size=20):
    config = {
        'version': 2,
        '$ref': '',
        'type': 'json',
        'description': f'fhir resources {objects}',
        'metadata': {'namespace': 'public', 'size': size, 'sep': ','},
    }
    properties = {}
    for name in objects:
        obj = getattr(stu3, name)
        schema = proto_schema(obj)
        properties[name] = {'type': 'json', 'metadata': {'size': size}, 'properties': to_fixture_schema(schema)}
    config['properties'] = properties
    return config

if __name__ == '__main__':
    print(yaml.dump(main(*sys.argv[1:]), indent=2))
