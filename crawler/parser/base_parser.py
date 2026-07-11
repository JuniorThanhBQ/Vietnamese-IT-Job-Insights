"""
Base HTML parser module using Selectolax.
Provides shared utility methods for extraction and JSON-LD parsing.
"""
import json
from typing import Optional
from selectolax.parser import HTMLParser, Node


class BaseParser:
    """
    Base parser wrapping Selectolax HTMLParser.
    Provides utility methods for safe text and attribute extraction.
    """

    def __init__(self, html: str):
        self.parser = HTMLParser(html)

    def css_first(self, selector: str) -> Optional[Node]:
        """Find the first matching node for a CSS selector."""
        return self.parser.css_first(selector)

    def css(self, selector: str) -> list[Node]:
        """Find all matching nodes for a CSS selector."""
        return self.parser.css(selector)

    def get_text(self, selector: str, default: Optional[str] = None) -> Optional[str]:
        """Safely extract text from the first matching node."""
        node = self.css_first(selector)
        if node is not None:
            return node.text(strip=True)
        return default

    def get_attribute(
        self, selector: str, attribute: str, default: Optional[str] = None
    ) -> Optional[str]:
        """Safely extract an attribute value from the first matching node."""
        node = self.css_first(selector)
        if node is not None:
            return node.attributes.get(attribute, default)
        return default

    def get_json_ld_job_posting(self) -> Optional[dict]:
        """Find, parse, and return the JobPosting JSON-LD dictionary if present."""
        for script in self.css("script[type='application/ld+json']"):
            try:
                data = json.loads(script.text(strip=True))
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if isinstance(item, dict) and item.get("@type") == "JobPosting":
                        return item
            # pylint: disable=broad-exception-caught
            except Exception:
                pass
        return None
