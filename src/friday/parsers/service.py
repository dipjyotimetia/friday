from typing import Dict, List

from google.protobuf.descriptor_pb2 import ServiceDescriptorProto


class ServiceParser:
    def __init__(self, service: ServiceDescriptorProto):
        self.service = service

    def parse(self) -> Dict:
        """Parse service descriptor into dictionary format"""
        return {"name": self.service.name, "methods": self._parse_methods()}

    def _parse_methods(self) -> List[Dict]:
        methods = []
        for method in self.service.method:
            methods.append(
                {
                    "name": method.name,
                    "input_type": method.input_type,
                    "output_type": method.output_type,
                    "client_streaming": method.client_streaming,
                    "server_streaming": method.server_streaming,
                }
            )
        return methods
