# pylint: disable=duplicate-code
import re
import hashlib
from typing import Optional
from crawler.parser.base_parser import BaseParser
from crawler.utils.normalizer import (
    normalize_salary,
    normalize_seniority,
    normalize_remote_policy,
    normalize_employment_type
)


class TopDevParser(BaseParser):
    """
    Parser for TopDev job details pages.
    Extracts company and job attributes from HTML using Selectolax.
    """

    def __init__(self, html: str, url: str):
        super().__init__(html)
        self.url = url

    def parse_source_id(self) -> str:
        """Extract TopDev job source ID from the URL."""
        # Example URL: https://topdev.vn/detail-jobs/python-developer-company-xyz-12345
        # We can extract the trailing ID "12345"
        match = re.search(r"-(\d+)$", self.url.rstrip("/"))
        if match:
            return match.group(1)
        return self.url.split("/")[-1]

    def parse_company_name(self) -> str:
        """Extract company name with fallbacks."""
        for selector in [".company-name", ".job-detail__company-name", "a.company-name", "h3.company-name"]:
            name = self.get_text(selector)
            if name:
                return name
        return "Unknown Company"

    def parse_company_logo(self) -> Optional[str]:
        """Extract company logo URL."""
        for selector in [".company-logo img", ".logo img", "img.logo"]:
            logo = self.get_attribute(selector, "src")
            if logo:
                return logo
        return None

    def parse_company_size(self) -> Optional[str]:
        """Extract company size."""
        for selector in [".company-size", ".company-info__size", "span.size"]:
            size = self.get_text(selector)
            if size:
                return size
        return None

    def parse_company_industry(self) -> Optional[str]:
        """Extract industry type."""
        for selector in [".company-industry", ".company-info__industry"]:
            ind = self.get_text(selector)
            if ind:
                return ind
        return None

    def parse_company_address(self) -> Optional[str]:
        """Extract company address."""
        for selector in [".company-address", ".address", ".job-details__address"]:
            addr = self.get_text(selector)
            if addr:
                return addr
        return None

    def parse_job_title(self) -> str:
        """Extract job title."""
        for selector in ["h1.job-title", ".job-detail__title", "h1.title-job", "h1"]:
            title = self.get_text(selector)
            if title:
                return title
        return "Untitled Job"

    def parse_salary_raw(self) -> Optional[str]:
        """Extract raw salary string."""
        for selector in [".salary", ".job-detail__salary", "span.salary", ".salary-value"]:
            sal = self.get_text(selector)
            if sal:
                return sal
        return "Thương lượng"

    def parse_job_description(self) -> str:
        """Extract job description text."""
        for selector in [".job-description", ".job-detail__description", "#job-description", ".description"]:
            desc = self.get_text(selector)
            if desc:
                return desc
        return "No description provided"

    def parse_job_requirements(self) -> Optional[str]:
        """Extract job requirements text."""
        for selector in [".job-requirements", ".job-detail__requirements", "#job-requirements", ".requirements"]:
            reqs = self.get_text(selector)
            if reqs:
                return reqs
        return None

    def parse_raw_text_for_tags(self) -> str:
        """Get all tags text or badge text to analyze seniority, remote policy, and type."""
        nodes = self.css(".job-tag") + self.css(".tag") + self.css(".badge") + self.css(".job-detail__tag")
        return " ".join([n.text(strip=True) for n in nodes])

    # pylint: disable=too-many-locals
    def parse(self) -> dict:
        """Compile and parse the complete HTML document into a standardized schema dict."""
        source_id = self.parse_source_id()
        company_name = self.parse_company_name()

        # Aggregate tags text for heuristic parsing
        tags_text = self.parse_raw_text_for_tags() + " " + self.parse_job_title()

        # Parse and normalize salary
        raw_salary = self.parse_salary_raw()
        sal_min, sal_max, currency, sal_raw = normalize_salary(raw_salary)

        # Normalize metadata
        seniority = normalize_seniority(tags_text)
        remote_policy = normalize_remote_policy(tags_text)
        employment_type = normalize_employment_type(tags_text)

        # Generate a unique content hash for change detection
        job_desc = self.parse_job_description()
        job_req = self.parse_job_requirements() or ""
        job_title = self.parse_job_title()

        content_str = f"{job_title}|{sal_raw}|{job_desc}|{job_req}"
        content_hash = hashlib.sha256(content_str.encode("utf-8")).hexdigest()

        return {
            "company": {
                "source_id": f"topdev-{company_name.lower().replace(' ', '-')}",
                "source_site": "topdev",
                "name": company_name,
                "logo_url": self.parse_company_logo(),
                "website_url": None,
                "company_size": self.parse_company_size(),
                "industry": self.parse_company_industry(),
                "address": self.parse_company_address(),
                "raw_metadata": {}
            },
            "job": {
                "source_id": source_id,
                "source_site": "topdev",
                "title": job_title,
                "url": self.url,
                "salary_min": sal_min,
                "salary_max": sal_max,
                "salary_currency": currency,
                "salary_raw": sal_raw,
                "seniority": seniority,
                "remote_policy": remote_policy,
                "employment_type": employment_type,
                "description": job_desc,
                "requirements": job_req if job_req else None,
                "posting_time": None,
                "expiry_time": None,
                "is_active": True,
                "content_hash": content_hash,
                "raw_metadata": {
                    "tags": tags_text.strip()
                }
            }
        }
