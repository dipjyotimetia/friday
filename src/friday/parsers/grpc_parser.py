from pathlib import Path
from typing import Dict, List

from google.protobuf import descriptor_pb2
from google.protobuf.compiler import parser

from .message import MessageParser
from .service import ServiceParser


class GrpcParser:
    def parse_file(self, proto_path: str) -> Dict:
        """Parse proto file and return service definitions"""
        file_descriptor = self._load_proto_file(proto_path)

        return {
            "package": file_descriptor.package,
            "services": self._parse_services(file_descriptor.service),
            "messages": self._parse_messages(file_descriptor.message_type),
        }

    def _load_proto_file(self, proto_path: str) -> descriptor_pb2.FileDescriptorProto:
        """Load and parse proto file"""
        proto_file = Path(proto_path).read_text()
        file_desc = descriptor_pb2.FileDescriptorProto()
        parser.Parser().ParseString(proto_file, file_desc)
        return file_desc

    def _parse_services(self, services) -> List[Dict]:
        """Parse all services in proto file"""
        return [ServiceParser(svc).parse() for svc in services]

    def _parse_messages(self, messages) -> List[Dict]:
        """Parse all messages in proto file"""
        return [MessageParser(msg).parse() for msg in messages]
