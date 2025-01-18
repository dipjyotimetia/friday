from typing import Dict

from prance import ResolvingParser


def parse_openapi_spec(spec_path: str) -> Dict:
    """Parse OpenAPI specification file"""
    parser = ResolvingParser(spec_path)
    return parser.specification
