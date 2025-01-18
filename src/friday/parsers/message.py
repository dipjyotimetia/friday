from typing import Dict, List

from google.protobuf.descriptor_pb2 import DescriptorProto, FieldDescriptorProto


class MessageParser:
    def __init__(self, message: DescriptorProto):
        self.message = message

    def parse(self) -> Dict:
        """Parse protobuf message into dictionary format"""
        return {
            "name": self.message.name,
            "fields": self._parse_fields(),
            "nested_types": self._parse_nested_types(),
        }

    def _parse_fields(self) -> List[Dict]:
        fields = []
        for field in self.message.field:
            fields.append(
                {
                    "name": field.name,
                    "number": field.number,
                    "type": FieldDescriptorProto.Type.Name(field.type),
                    "label": FieldDescriptorProto.Label.Name(field.label),
                }
            )
        return fields

    def _parse_nested_types(self) -> List[Dict]:
        nested = []
        for msg in self.message.nested_type:
            nested.append(MessageParser(msg).parse())
        return nested
