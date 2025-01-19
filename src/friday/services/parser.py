import logging
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class WebCrawler:
    def __init__(self, max_pages: int = 10, same_domain_only: bool = True):
        self.visited_urls = set()
        self.max_pages = max_pages
        self.same_domain_only = same_domain_only

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        return urlparse(url).netloc

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all links from the page"""
        links = []
        domain = self._get_domain(base_url)

        for link in soup.find_all("a", href=True):
            url = urljoin(base_url, link["href"])
            # Skip non-HTTP(S) links
            if not url.startswith(("http://", "https://")):
                continue
            # Check if we should only crawl same domain
            if self.same_domain_only and domain != self._get_domain(url):
                continue
            links.append(url)
        return links

    def extract_text_from_url(self, url: str) -> Optional[Dict[str, str]]:
        """Extract text content from a webpage"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text and clean it
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)

            return {
                "url": url,
                "text": text,
                "title": soup.title.string if soup.title else "",
            }
        except Exception as e:
            logger.error(f"Failed to extract text from {url}: {str(e)}")
            return None

    def crawl(self, start_url: str) -> List[Dict[str, str]]:
        """Crawl pages starting from a URL"""
        pages_data = []
        to_visit = [start_url]

        while to_visit and len(self.visited_urls) < self.max_pages:
            url = to_visit.pop(0)

            if url in self.visited_urls:
                continue

            self.visited_urls.add(url)
            logger.info(f"Crawling {url}")

            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

                # Extract text from current page
                page_data = self.extract_text_from_url(url)
                if page_data:
                    pages_data.append(page_data)

                # Get links for next pages
                links = self._extract_links(soup, url)
                to_visit.extend(
                    [link for link in links if link not in self.visited_urls]
                )

            except Exception as e:
                logger.error(f"Error crawling {url}: {str(e)}")
                continue

        return pages_data
