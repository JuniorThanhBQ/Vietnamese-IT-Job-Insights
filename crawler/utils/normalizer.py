"""
Utility module for normalizing and cleaning crawled job and company data.
Provides functions to format salary, seniority, remote policy, and clean HTML.
"""
import re
from typing import Optional, Tuple

# pylint: disable=too-many-return-statements


def normalize_salary(
    salary_str: Optional[str]
) -> Tuple[Optional[float], Optional[float], str, str]:
    """
    Parses and normalizes salary string to min_salary, max_salary, and currency.
    Examples:
      - "1,000 - 2,500 USD" -> (1000.0, 2500.0, "USD", "1,000 - 2,500 USD")
      - "30 - 50 triệu VND" -> (30000000.0, 50000000.0, "VND", "30 - 50 triệu VND")
      - "Up to 1,500 USD" -> (None, 1500.0, "USD", "Up to 1,500 USD")
      - "Thương lượng" or None -> (None, None, "VND", "Thương lượng")
    """
    if not salary_str:
        return None, None, "VND", "Thương lượng"

    raw_str = salary_str.strip()
    s_lower = raw_str.lower()

    # Detect currency
    if "usd" in s_lower or "$" in s_lower:
        currency = "USD"
    else:
        currency = "VND"

    # Clean punctuation except hyphens/dots
    # Remove commas used in numbers (e.g. 1,000 -> 1000)
    cleaned = s_lower.replace(",", "")

    # Extract all numbers/decimals
    numbers = re.findall(r"\d+(?:\.\d+)?", cleaned)

    if not numbers:
        return None, None, currency, raw_str

    # Convert to float list
    values = [float(n) for n in numbers]

    # Check for multiplier (e.g. "triệu", "m", "k")
    multiplier = 1.0
    if "triệu" in s_lower or "trieu" in s_lower or "tr" in s_lower or "m" in s_lower:
        multiplier = 1000000.0
    elif "k" in s_lower and currency == "USD":
        # e.g., "1k - 2k USD"
        multiplier = 1000.0
    elif "k" in s_lower and currency == "VND":
        # e.g., "500k - 800k VND"
        multiplier = 1000.0

    # Scale values by multiplier
    values = [val * multiplier for val in values]

    if len(values) >= 2:
        return values[0], values[1], currency, raw_str

    if len(values) == 1:
        # Check if it specifies "up to" or "tối đa" or "under"
        max_terms = ["up to", "to", "tối đa", "toi da", "dưới", "under", "max"]
        if any(term in s_lower for term in max_terms):
            return None, values[0], currency, raw_str
        # Or "from" or "tối thiểu" or "above"
        min_terms = ["from", "tối thiểu", "toi thieu", "trên", "above", "min"]
        if any(term in s_lower for term in min_terms):
            return values[0], None, currency, raw_str

        return values[0], values[0], currency, raw_str

    return None, None, currency, raw_str


def normalize_seniority(text: Optional[str]) -> str:
    """
    Normalizes seniority level against DB allowed values:
    'Intern', 'Fresher', 'Junior', 'Middle', 'Senior', 'Lead', 'Manager', 'Unknown'
    """
    if not text:
        return "Unknown"

    s_lower = text.lower()
    if "intern" in s_lower or "thực tập" in s_lower:
        return "Intern"
    if "fresher" in s_lower or "mới tốt nghiệp" in s_lower:
        return "Fresher"
    if "junior" in s_lower:
        return "Junior"
    if "middle" in s_lower:
        return "Middle"
    if "senior" in s_lower:
        return "Senior"
    if "lead" in s_lower or "trưởng nhóm" in s_lower:
        return "Lead"
    if "manager" in s_lower or "quản lý" in s_lower or "director" in s_lower:
        return "Manager"

    return "Unknown"


def normalize_remote_policy(text: Optional[str]) -> str:
    """
    Normalizes remote policy against DB allowed values:
    'Remote', 'Hybrid', 'Onsite', 'Unknown'
    """
    if not text:
        return "Unknown"

    s_lower = text.lower()
    if "hybrid" in s_lower or "linh hoạt" in s_lower:
        return "Hybrid"
    if "remote" in s_lower or "làm việc từ xa" in s_lower or "tự do" in s_lower:
        return "Remote"
    if "onsite" in s_lower or "office" in s_lower or "văn phòng" in s_lower or "tại chỗ" in s_lower:
        return "Onsite"

    return "Unknown"


def normalize_employment_type(text: Optional[str]) -> str:
    """
    Normalizes employment type against DB allowed values:
    'Full-time', 'Part-time', 'Contract', 'Internship', 'Unknown'
    """
    if not text:
        return "Unknown"

    s_lower = text.lower()
    if "full-time" in s_lower or "fulltime" in s_lower or "toàn thời gian" in s_lower:
        return "Full-time"
    if "part-time" in s_lower or "parttime" in s_lower or "bán thời gian" in s_lower:
        return "Part-time"
    if "contract" in s_lower or "hợp đồng" in s_lower or "freelance" in s_lower:
        return "Contract"
    if "intern" in s_lower or "thực tập" in s_lower:
        return "Internship"

    return "Unknown"


def clean_html(html_str: Optional[str]) -> str:
    """
    Strips HTML tags from description/requirements and normalizes spacing.
    Preserves line breaks for readability.
    """
    if not html_str:
        return ""
    # pylint: disable=import-outside-toplevel
    from selectolax.parser import HTMLParser

    # Unescape HTML entities (e.g. &nbsp;, &quot;)
    import html
    unescaped = html.unescape(html_str)

    parser = HTMLParser(unescaped)
    text = parser.text(deep=True, separator="\n")

    # Split, clean whitespace, and filter empty lines
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join([line for line in lines if line])
