import logging
from typing import Dict

from atlassian import Confluence
from bs4 import BeautifulSoup
from retrying import retry

from friday.config.config import (
    CONFLUENCE_API_TOKEN,
    CONFLUENCE_URL,
    CONFLUENCE_USERNAME,
)

logger = logging.getLogger(__name__)


class HTMLConverter:
    def handle(self, html_content: str) -> str:
        """Convert Confluence storage format HTML to plain text"""
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text()


class ConfluenceConnector:
    def __init__(self):
        self.client = Confluence(
            url=CONFLUENCE_URL,
            username=CONFLUENCE_USERNAME,
            password=CONFLUENCE_API_TOKEN,
        )
        self.html_converter = HTMLConverter()

    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def get_page_content(self, page_id: str, format: str = "storage") -> str:
        """
        Get page content in specified format
        Args:
            page_id: Confluence page ID
            format: Content format (storage, view, export_view, styled_view)
        """
        try:
            page = self.client.get_page_by_id(page_id, expand=f"body.{format}")
            content = page["body"][format]["value"]
            return (
                self.html_converter.handle(content) if format == "storage" else content
            )
        except Exception as e:
            logger.error(f"Error fetching page {page_id}: {str(e)}")
            raise

    def get_page_properties(self, page_id: str) -> Dict:
        """Get page properties including labels, restrictions, and version info"""
        try:
            return self.client.get_page_by_id(
                page_id,
                expand="version,ancestors,descendants,space,metadata.labels,restrictions",
            )
        except Exception as e:
            logger.error(f"Error fetching properties for page {page_id}: {str(e)}")
            raise
