import logging
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

from scrapy.crawler import CrawlerProcess
from scrapy.http import Response
from scrapy.spiders import Spider

logger = logging.getLogger(__name__)


class WebCrawler:
    def __init__(self, max_pages: int = 10, same_domain_only: bool = True):
        self.visited_urls: Set[str] = set()
        self.max_pages = max_pages
        self.same_domain_only = same_domain_only
        self.pages_data: List[Dict[str, str]] = []

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        return urlparse(url).netloc

    class _CustomSpider(Spider):
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
            super().__init__(*args, **kwargs)
            self.start_urls = [start_url]
            self.crawler_instance = crawler_instance

            # Set allowed domains if same_domain_only is True
            if self.crawler_instance.same_domain_only:
                self.allowed_domains = [self.crawler_instance._get_domain(start_url)]

        def parse(self, response: Response):
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
                logger.error(f"Error parsing {url}: {str(e)}")

    def extract_text_from_url(self, response: Response) -> Optional[Dict[str, str]]:
        """Extract text content from a webpage"""
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
        """Crawl pages starting from a URL"""
        # Reset state for new crawl
        self.visited_urls.clear()
        self.pages_data.clear()

        # Configure and run the crawler
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
