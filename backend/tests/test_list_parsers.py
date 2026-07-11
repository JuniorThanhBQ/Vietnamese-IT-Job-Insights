import sys
import os

# Add root directory to python path to import crawler
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from crawler.parser.itviec_list_parser import ITViecListParser
from crawler.parser.topdev_list_parser import TopDevListParser


def test_itviec_list_parser():
    mock_html = """
    <html>
        <body>
            <div class="job-list">
                <a href="/jobs/python-developer-company-a-1234?search=true">Python Job A</a>
                <a href="/jobs/golang-developer-company-b-5678">Go Job B</a>
                <a href="/companies/company-a">Company profile</a>
            </div>
            <div class="pagination">
                <a href="/it-jobs?page=2" rel="next">Next</a>
            </div>
        </body>
    </html>
    """
    parser = ITViecListParser(mock_html, base_url="https://itviec.com")
    urls = parser.parse_job_urls()
    assert len(urls) == 2
    assert "https://itviec.com/jobs/python-developer-company-a-1234" in urls
    assert "https://itviec.com/jobs/golang-developer-company-b-5678" in urls
    assert parser.has_next_page() is True


def test_topdev_list_parser():
    mock_html = """
    <html>
        <body>
            <div class="jobs">
                <a href="/detail-jobs/backend-engineer-node-company-x-9999?source=search">Node Job</a>
                <a href="/detail-jobs/frontend-engineer-react-company-y-8888">React Job</a>
                <a href="/blog/career-advice">Blog post</a>
            </div>
            <div class="pagination">
                <a href="/viec-lam-it?page=2">Trang sau</a>
            </div>
        </body>
    </html>
    """
    parser = TopDevListParser(mock_html, base_url="https://topdev.vn")
    urls = parser.parse_job_urls()
    assert len(urls) == 2
    assert "https://topdev.vn/detail-jobs/backend-engineer-node-company-x-9999" in urls
    assert (
        "https://topdev.vn/detail-jobs/frontend-engineer-react-company-y-8888" in urls
    )
    assert parser.has_next_page() is True
