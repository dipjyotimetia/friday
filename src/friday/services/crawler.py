import logging
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)


class WebCrawler:
    def __init__(
        self,
        max_pages: int = 10,
        same_domain_only: bool = True,
        auth: Optional[Dict[str, str]] = None,
    ):
        self.visited_urls = set()
        self.max_pages = max_pages
        self.same_domain_only = same_domain_only
        self.auth = auth

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
        """Extract text content from a URL"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            return {"url": url, "text": text}
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def crawl(self, start_url: str) -> List[Dict[str, str]]:
        """Crawl web pages starting from the given URL"""
        pages_data = []
        urls_to_visit = [start_url]

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            if self.auth:
                page.authenticate(self.auth)

            while urls_to_visit and len(pages_data) < self.max_pages:
                url = urls_to_visit.pop(0)
                if url in self.visited_urls:
                    continue

                self.visited_urls.add(url)
                logger.info(f"Crawling {url}")

                try:
                    page.goto(url)
                    page_content = page.content()
                    soup = BeautifulSoup(page_content, "html.parser")
                    text = soup.get_text(separator="\n", strip=True)
                    pages_data.append({"url": url, "text": text})

                    links = self._extract_links(soup, url)
                    urls_to_visit.extend(links)
                except Exception as e:
                    logger.error(f"Failed to crawl {url}: {e}")

            browser.close()

        return pages_data
