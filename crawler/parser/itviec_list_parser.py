# pylint: disable=duplicate-code
"""
Parser for extracting job listing links from ITviec list pages.
Supports both standard /it-jobs/ links and /sign_in?job= wrapped links.
"""
import re
from urllib.parse import urljoin, urlparse, parse_qs
from crawler.parser.base_parser import BaseParser


class ITViecListParser(BaseParser):
    """
    Parser for ITviec job list pages.
    Extracts job detail URLs from list HTML.
    """

    def __init__(self, html: str, base_url: str = "https://itviec.com"):
        super().__init__(html)
        self.base_url = base_url

    def parse_job_urls(self) -> list[str]:
        """Extract all job detail URLs from the list page."""
        urls = []
        for a_node in self.css("a"):
            href = a_node.attributes.get("href")
            if not href:
                continue

            clean_url = None

            # Strategy 1: Standard job detail URL
            if "/it-jobs/" in href or "/jobs/" in href:
                full_url = urljoin(self.base_url, href)
                clean_url = full_url.split("?")[0].rstrip("/")

            # Strategy 2: Sign-in wrapped job detail URL
            elif "/sign_in" in href and "job=" in href:
                try:
                    parsed_url = urlparse(href)
                    query_params = parse_qs(parsed_url.query)
                    job_slugs = query_params.get("job")
                    if job_slugs:
                        slug = job_slugs[0]
                        clean_url = f"https://itviec.com/it-jobs/{slug}"
                except Exception:  # pylint: disable=broad-exception-caught
                    pass

            # Validate and add
            if clean_url:
                if re.search(r"-(\d+)$", clean_url):
                    if clean_url not in urls:
                        urls.append(clean_url)
        return urls

    def has_next_page(self) -> bool:
        """Check if there is a next page link in pagination."""
        for a_node in self.css("a"):
            if a_node.attributes.get("rel") == "next":
                return True
            text = a_node.text(strip=True).lower()
            if "next" in text or "trang sau" in text:
                return True
        return False
