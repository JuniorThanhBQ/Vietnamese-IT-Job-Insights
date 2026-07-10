import os
import sys
from loguru import logger

# Add backend directory and root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from crawler.parser.itviec_parser import ITViecParser
from crawler.parser.topdev_parser import TopDevParser


def test_itviec_parser():
    mock_html = """
    <html>
        <body>
            <h1 class="job-details__title">Senior Python Developer</h1>
            <div class="company-name-container">
                <h3>XYZ Tech Company</h3>
            </div>
            <div class="company-logo"><img src="https://example.com/logo.png" /></div>
            <div class="company-size">150-300 employees</div>
            <div class="company-industry">Software Development</div>
            <div class="company-address">District 1, Ho Chi Minh City</div>
            <div class="salary-value">1,500 - 3,000 USD</div>
            <div class="job-details__description">We are looking for Python developers.</div>
            <div class="job-details__requirements">Must have 5 years experience.</div>
            <span class="job-details__tag">Hybrid</span>
            <span class="job-details__tag">Full-time</span>
            <span class="badge">Senior</span>
        </body>
    </html>
    """
    url = "https://itviec.com/jobs/senior-python-developer-xyz-tech-1234"
    parser = ITViecParser(mock_html, url)
    result = parser.parse()

    logger.info("ITViec Parser Test Results:")
    logger.info(f"Company Name: {result['company']['name']}")
    logger.info(f"Job Title: {result['job']['title']}")
    logger.info(f"Salary Min: {result['job']['salary_min']} | Max: {result['job']['salary_max']} | Currency: {result['job']['salary_currency']}")
    logger.info(f"Seniority: {result['job']['seniority']}")
    logger.info(f"Remote Policy: {result['job']['remote_policy']}")
    logger.info(f"Employment Type: {result['job']['employment_type']}")

    # Asserts
    assert result["company"]["name"] == "XYZ Tech Company"
    assert result["job"]["title"] == "Senior Python Developer"
    assert result["job"]["salary_min"] == 1500.0
    assert result["job"]["salary_max"] == 3000.0
    assert result["job"]["salary_currency"] == "USD"
    assert result["job"]["seniority"] == "Senior"
    assert result["job"]["remote_policy"] == "Hybrid"
    assert result["job"]["employment_type"] == "Full-time"
    logger.success("ITViec Parser test passed successfully!")


def test_topdev_parser():
    mock_html = """
    <html>
        <body>
            <h1 class="job-title">Middle Go Developer</h1>
            <div class="company-name">ABC Corp</div>
            <div class="company-logo"><img src="https://example.com/abc-logo.png" /></div>
            <div class="company-size">50-100 employees</div>
            <div class="company-address">Cau Giay, Hanoi</div>
            <div class="salary">30 - 50 triệu VND</div>
            <div class="job-description">We need Go engineers.</div>
            <div class="job-requirements">Go, PostgreSQL experience.</div>
            <span class="job-tag">Remote</span>
            <span class="badge">Full-time</span>
            <span class="badge">Middle</span>
        </body>
    </html>
    """
    url = "https://topdev.vn/detail-jobs/middle-go-developer-abc-corp-56789"
    parser = TopDevParser(mock_html, url)
    result = parser.parse()

    logger.info("TopDev Parser Test Results:")
    logger.info(f"Company Name: {result['company']['name']}")
    logger.info(f"Job Title: {result['job']['title']}")
    logger.info(f"Salary Min: {result['job']['salary_min']} | Max: {result['job']['salary_max']} | Currency: {result['job']['salary_currency']}")
    logger.info(f"Seniority: {result['job']['seniority']}")
    logger.info(f"Remote Policy: {result['job']['remote_policy']}")
    logger.info(f"Employment Type: {result['job']['employment_type']}")

    # Asserts
    assert result["company"]["name"] == "ABC Corp"
    assert result["job"]["title"] == "Middle Go Developer"
    assert result["job"]["salary_min"] == 30000000.0
    assert result["job"]["salary_max"] == 50000000.0
    assert result["job"]["salary_currency"] == "VND"
    assert result["job"]["seniority"] == "Middle"
    assert result["job"]["remote_policy"] == "Remote"
    assert result["job"]["employment_type"] == "Full-time"
    logger.success("TopDev Parser test passed successfully!")


if __name__ == "__main__":
    logger.info("Running parser integration tests...")
    test_itviec_parser()
    test_topdev_parser()
    logger.success("All parser tests completed successfully!")
