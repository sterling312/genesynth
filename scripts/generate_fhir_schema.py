"""
support script to convert google fhir object to schema yaml
note that this has google-fhir==0.7.3 dependency, which only works with python<=3.9
"""

import sys
import json
from proto.google.fhir.proto.stu3 import resources_pb2 as stu3, datatypes_pb2 as fhir_type, codes_pb2 as stu3_code
from google.protobuf import descriptor, json_format

#sys.setrecursionlimit(10000)

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

FHIR_TYPES = {
    # datatypes.proto
    'String': 'string',
    'Extension': 'json',
    'Id': 'string',
    'Instant': 'timestamp',
    'Uri': 'string',
    'DateTime': 'datetime',
    'Decimal': 'decimal',
    'Boolean': 'boolean',
    'Integer': 'integer',
    'Date': 'date',
    'Time': 'time',
    'MimeTypeCode': 'string',
    'LanguageCode': 'string',
    'Base64Binary': 'string', # This will be changed to bytes when tye type is supported
    'UnsignedInt': 'integer',
    'Coding': 'json',
    'Xhtml': 'string',
    'IdentifierUseCode': 'string',
    'CodeableConcept': 'json',
    'Period': 'object',
    'Reference': 'string',
    'QuantityComparatorCode': 'string',
    'Code': 'string',
    'Attachment': 'json',
    'Quantity': 'decimal',
    # codes.proto
    'NarrativeStatusCode': 'string',
    'QuestionnaireItemTypeCode': 'string',
    # resources.proto
    'ContainedResource': 'json',
    'Answer': 'object',
    'Value': 'object',
    'EnableWhen': 'object',
    'Option': 'object',
    'Initial': 'object',
    'Item': 'object',
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
        schema[field.name] = type_inspector(field)
    return schema

def proto_to_dict(message):
    return json_format.MessageToDict(message, including_default_value_fields=True)

if __name__ == '__main__':
    print(json.dumps(proto_schema(getattr(stu3, sys.argv[1]))))
