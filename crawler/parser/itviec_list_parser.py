# pylint: disable=duplicate-code
from urllib.parse import urljoin
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
            if href and "/jobs/" in href:
                full_url = urljoin(self.base_url, href)
                clean_url = full_url.split("?")[0].rstrip("/")
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
