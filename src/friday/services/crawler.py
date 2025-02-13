"""
Web Crawler Module

This module provides a web crawling service using Scrapy framework with real-time logging
capabilities over WebSocket connections. It supports configurable crawling behavior and
content extraction.

Features:
- Configurable maximum page limit
- Domain restriction options
- Real-time progress logging via WebSocket
- Robust error handling
- Text content extraction
- Robotstxt compliance
- Rate limiting and polite crawling

Example:
    >>> crawler = WebCrawler(max_pages=5, same_domain_only=True)
    >>> results = crawler.crawl("https://example.com")
"""

import logging
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

from scrapy.crawler import CrawlerProcess
from scrapy.http import Response
from scrapy.spiders import Spider

from friday.services.logger import ws_logger

logger = logging.getLogger(__name__)


class WebCrawler:
    """
    A configurable web crawler built on Scrapy with real-time logging.

    This class provides functionality for crawling web pages, extracting content,
    and managing the crawling process with various restrictions and configurations.

    Attributes:
        visited_urls (Set[str]): Set of URLs that have been crawled
        max_pages (int): Maximum number of pages to crawl
        same_domain_only (bool): Whether to restrict crawling to the same domain
        pages_data (List[Dict[str, str]]): Collected data from crawled pages
    """

    def __init__(self, max_pages: int = 10, same_domain_only: bool = True):
        """
        Initialize the web crawler with configurable parameters.

        Args:
            max_pages (int): Maximum number of pages to crawl (default: 10)
            same_domain_only (bool): Whether to restrict crawling to the same domain (default: True)

        Example:
            >>> crawler = WebCrawler(max_pages=5, same_domain_only=True)
        """
        self.visited_urls: Set[str] = set()
        self.max_pages = max_pages
        self.same_domain_only = same_domain_only
        self.pages_data: List[Dict[str, str]] = []

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        return urlparse(url).netloc

    class _CustomSpider(Spider):
        """
        Custom Scrapy spider implementation for controlled web crawling.

        This inner class handles the actual crawling process with configurable
        settings and proper rate limiting.

        Attributes:
            name (str): Name of the spider
            custom_settings (dict): Scrapy spider configuration
        """

        name = "compatible_crawler"

        custom_settings = {
            "ROBOTSTXT_OBEY": True,
            "CONCURRENT_REQUESTS": 16,
            "DOWNLOAD_DELAY": 1,
            "COOKIES_ENABLED": False,
            "USER_AGENT": "Mozilla/5.0 (compatible; CustomBot/1.0)",
        }

        def __init__(
            self, start_url: str, crawler_instance: "WebCrawler", *args, **kwargs
        ):
            """
            Initialize the spider with start URL and crawler instance.

            Args:
                start_url (str): The initial URL to start crawling from
                crawler_instance (WebCrawler): Reference to the parent crawler
                *args: Variable length argument list
                **kwargs: Arbitrary keyword arguments
            """
            super().__init__(*args, **kwargs)
            self.start_urls = [start_url]
            self.crawler_instance = crawler_instance

            # Set allowed domains if same_domain_only is True
            if self.crawler_instance.same_domain_only:
                self.allowed_domains = [self.crawler_instance._get_domain(start_url)]

        async def _send_log(self, message: str) -> None:
            """Send log message to websocket with error handling"""
            try:
                if ws_logger:
                    await ws_logger.broadcast(message)  # Call broadcast directly
                else:
                    print(f"Warning: WebSocket logger not initialized: {message}")
            except Exception as e:
                print(f"Error sending log: {message} - {str(e)}")

        async def parse(self, response: Response):
            """Parse webpage and extract content"""
            url = response.url

            # Skip if already visited or max pages reached
            if (
                url in self.crawler_instance.visited_urls
                or len(self.crawler_instance.visited_urls)
                >= self.crawler_instance.max_pages
            ):
                return

            self.crawler_instance.visited_urls.add(url)
            logger.info(f"Crawling {url}")
            await self._send_log(f"Crawling {url}")

            try:
                # Extract text content
                page_data = self.crawler_instance.extract_text_from_url(response)
                if page_data:
                    self.crawler_instance.pages_data.append(page_data)

                # Extract and follow links
                if (
                    len(self.crawler_instance.visited_urls)
                    < self.crawler_instance.max_pages
                ):
                    domain = self.crawler_instance._get_domain(url)

                    for href in response.css("a::attr(href)").getall():
                        next_url = urljoin(response.url, href)

                        # Skip non-HTTP(S) links
                        if not next_url.startswith(("http://", "https://")):
                            continue

                        # Check domain restriction
                        if (
                            self.crawler_instance.same_domain_only
                            and domain != self.crawler_instance._get_domain(next_url)
                        ):
                            continue

                        if next_url not in self.crawler_instance.visited_urls:
                            yield response.follow(next_url, self.parse)

            except Exception as e:
                await self._send_log(f"Error parsing {url}: {str(e)}")
                logger.error(f"Error parsing {url}: {str(e)}")

    def extract_text_from_url(self, response: Response) -> Optional[Dict[str, str]]:
        """
        Extract text content from a webpage response.

        Args:
            response (Response): Scrapy response object containing the webpage

        Returns:
            Optional[Dict[str, str]]: Dictionary containing URL, text content, and title
                                    or None if extraction fails

        Example:
            >>> data = crawler.extract_text_from_url(response)
            >>> if data:
            ...     print(f"Title: {data['title']}")
        """
        try:
            # Remove script and style elements
            body = response.css("body").get()
            if not body:
                return None

            # Extract text content
            text_content = " ".join(
                [
                    text.strip()
                    for text in response.xpath("//body//text()").getall()
                    if text.strip() and not text.strip().isspace()
                ]
            )

            return {
                "url": response.url,
                "text": text_content,
                "title": response.css("title::text").get("").strip(),
            }
        except Exception as e:
            logger.error(f"Failed to extract text from {response.url}: {str(e)}")
            return None

    def crawl(self, start_url: str) -> List[Dict[str, str]]:
        """
        Start crawling from a specified URL.

        Args:
            start_url (str): The URL to start crawling from

        Returns:
            List[Dict[str, str]]: List of dictionaries containing extracted data
                                 from crawled pages

        Example:
            >>> crawler = WebCrawler(max_pages=5)
            >>> results = crawler.crawl("https://example.com")
            >>> for page in results:
            ...     print(f"Found page: {page['url']}")
        """

        self.visited_urls.clear()
        self.pages_data.clear()

        process = CrawlerProcess(
            {
                "LOG_LEVEL": "ERROR",
                "ROBOTSTXT_OBEY": True,
                "COOKIES_ENABLED": False,
            }
        )

        process.crawl(self._CustomSpider, start_url=start_url, crawler_instance=self)
        process.start()

        return self.pages_data
