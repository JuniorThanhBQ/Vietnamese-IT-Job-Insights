# pylint: disable=duplicate-code
"""
Parser module for TopDev job details page.
Uses a hybrid JSON-LD and semantic text-based matching strategy.
"""
import re
import hashlib
from datetime import datetime
from typing import Optional
from crawler.parser.base_parser import BaseParser
from crawler.utils.normalizer import (
    normalize_salary,
    normalize_seniority,
    normalize_remote_policy,
    normalize_employment_type,
    clean_html
)


class TopDevParser(BaseParser):
    """
    Parser for TopDev job details pages.
    Extracts company and job attributes from HTML using Selectolax and JSON-LD.
    """

    def __init__(self, html: str, url: str):
        super().__init__(html)
        self.url = url
        self.json_ld = self.get_json_ld_job_posting()

    def parse_source_id(self) -> str:
        """Extract TopDev job source ID from the URL."""
        match = re.search(r"-(\d+)$", self.url.rstrip("/"))
        if match:
            return match.group(1)
        return self.url.split("/")[-1]

    def _parse_json_ld_address(self) -> Optional[str]:
        """Extract job address from JSON-LD location field."""
        if not self.json_ld:
            return None
        loc = self.json_ld.get("jobLocation")
        if not loc:
            return None
        if isinstance(loc, list):
            loc = loc[0]
        addr = loc.get("address")
        if not addr:
            return None
        if isinstance(addr, str):
            return addr

        parts = []
        fields = [
            "streetAddress",
            "addressLocality",
            "addressRegion",
            "addressCountry"
        ]
        for field in fields:
            val = addr.get(field)
            if val:
                parts.append(val)
        return ", ".join(parts) if parts else None

    def parse_company_name(self) -> str:
        """Extract company name with fallbacks."""
        if self.json_ld:
            name = self.json_ld.get("hiringOrganization", {}).get("name")
            if name:
                return name.strip()

        # Fallback selectors
        selectors = [
            "a[href*='/companies/'] span.text-brand-500",
            ".company-name",
            ".job-detail__company-name",
            "a.company-name"
        ]
        for selector in selectors:
            name = self.get_text(selector)
            if name:
                return name.strip()
        return "Unknown Company"

    def parse_company_logo(self) -> Optional[str]:
        """Extract company logo URL."""
        if self.json_ld:
            logo = self.json_ld.get("hiringOrganization", {}).get("logo")
            if logo:
                return logo.strip()

        # Fallback selectors
        selectors = [
            "img[alt='job-image'][class*='h-[72px]']",
            "img[alt='job-image']",
            ".company-logo img",
            ".logo img"
        ]
        for selector in selectors:
            logo = self.get_attribute(selector, "src")
            if logo:
                return logo.strip()
        return None

    def parse_company_size(self) -> Optional[str]:
        """Extract company size using text-based matching and fallback."""
        for node in self.css("span, div, p"):
            text = node.text(strip=True).strip().lower()
            if text in ["size", "company size", "quy mô"]:
                parent = node.parent
                if parent:
                    spans = parent.css("span, div, p")
                    for s in spans:
                        val = s.text(strip=True)
                        if val.lower() not in ["size", "company size", "quy mô"] and val:
                            return val
        return None

    def parse_company_industry(self) -> Optional[str]:
        """Extract industry type using text-based matching and fallback."""
        for node in self.css("span, div, p"):
            text = node.text(strip=True).strip().lower()
            if text in ["industry", "company industry", "ngành nghề"]:
                parent = node.parent
                if parent:
                    spans = parent.css("span, div, p")
                    for s in spans:
                        val = s.text(strip=True)
                        key_labels = ["industry", "company industry", "ngành nghề"]
                        if val.lower() not in key_labels and val:
                            return val
        return None

    def parse_company_address(self) -> Optional[str]:
        """Extract company address."""
        addr = self._parse_json_ld_address()
        if addr:
            return addr.strip()

        # Fallback selectors
        selectors = [
            ".company-address",
            ".address",
            ".job-details__address",
            "div.md\\:my-2 span.line-clamp-1"
        ]
        for selector in selectors:
            addr = self.get_text(selector)
            if addr:
                return addr.strip()
        return None

    def parse_job_title(self) -> str:
        """Extract job title."""
        if self.json_ld:
            title = self.json_ld.get("title")
            if title:
                return title.strip()

        selectors = [
            "a[class*='text-[18px]']",
            "a.text-text-700",
            "h1.job-title",
            ".job-detail__title"
        ]
        for selector in selectors:
            title = self.get_text(selector)
            if title:
                return title.strip()
        return "Untitled Job"

    def parse_salary_raw(self) -> Optional[str]:
        """Extract raw salary string."""
        if self.json_ld:
            val = self.json_ld.get("baseSalary", {}).get("value")
            if isinstance(val, dict):
                val = val.get("value")
            if val and val != "Negotiable":
                return str(val).strip()

        selectors = [
            "span.cursor-pointer",
            ".salary",
            ".job-detail__salary",
            "span.salary"
        ]
        for selector in selectors:
            sal = self.get_text(selector)
            if sal:
                return sal.strip()
        return "Thương lượng"

    def parse_job_description(self) -> str:
        """Extract job description text."""
        if self.json_ld:
            desc = self.json_ld.get("description")
            if desc:
                return desc.strip()

        selectors = [
            ".job-description",
            ".job-detail__description",
            "#job-description",
            ".description"
        ]
        for selector in selectors:
            desc = self.get_text(selector)
            if desc:
                return desc.strip()
        return "No description provided"

    def parse_job_requirements(self) -> Optional[str]:
        """Extract job requirements text."""
        # Check in DOM for h3 tags like REQUIREMENTS
        for h3 in self.css("h3"):
            h3_text = h3.text(strip=True).upper()
            if "REQUIREMENTS" in h3_text or "YÊU CẦU" in h3_text:
                parent = h3.parent
                if parent:
                    return parent.text(strip=True).replace(h3.text(strip=True), "", 1).strip()

        selectors = [
            ".job-requirements",
            ".job-detail__requirements",
            "#job-requirements",
            ".requirements"
        ]
        for selector in selectors:
            reqs = self.get_text(selector)
            if reqs:
                return reqs.strip()
        return None

    def parse_raw_text_for_tags(self) -> str:
        """Get all tags text or badge text to analyze seniority, remote policy, and type."""
        if self.json_ld:
            skills = self.json_ld.get("skills")
            if skills:
                return str(skills)

        selectors = [".job-tag", ".tag", ".badge", ".job-detail__tag"]
        nodes = []
        for selector in selectors:
            nodes.extend(self.css(selector))
        return " ".join([n.text(strip=True) for n in nodes])

    def _parse_date(self, key: str) -> Optional[datetime]:
        """Safely parse JSON-LD date field."""
        if not self.json_ld:
            return None
        date_str = self.json_ld.get(key)
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str)
        # pylint: disable=broad-exception-caught
        except Exception:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            # pylint: disable=broad-exception-caught
            except Exception:
                return None

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
        job_desc = clean_html(self.parse_job_description())
        job_req = clean_html(self.parse_job_requirements() or "")
        job_title = self.parse_job_title()

        content_str = f"{job_title}|{sal_raw}|{job_desc}|{job_req}"
        content_hash = hashlib.sha256(content_str.encode("utf-8")).hexdigest()

        posting_time = self._parse_date("datePosted")
        expiry_time = self._parse_date("validThrough")

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
                "posting_time": posting_time,
                "expiry_time": expiry_time,
                "is_active": True,
                "content_hash": content_hash,
                "raw_metadata": {
                    "tags": tags_text.strip()
                }
            }
        }
