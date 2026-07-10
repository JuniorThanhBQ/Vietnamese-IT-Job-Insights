import os
import sys
from typing import Optional
from loguru import logger

# Add backend directory to path so we can import app modules
# pylint: disable=wrong-import-position
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

from app.models.database import AsyncSessionLocal
from app.modules.companies.repository import CompanyRepository
from app.modules.companies.models import CompanyCreate
from app.modules.jobs.services import JobService
from app.modules.jobs.models import JobCreate

from crawler.base.crawler import BaseCrawler
from crawler.parser.itviec_parser import ITViecParser
from crawler.parser.topdev_parser import TopDevParser


class JobPipeline:
    """
    Scrapes job posting URLs, parses contents using Selectolax,
    and upserts companies and jobs into the SQLAlchemy database.
    """

    def __init__(self, crawler: Optional[BaseCrawler] = None):
        self.crawler = crawler or BaseCrawler()

    # pylint: disable=broad-exception-caught
    async def process_url(self, url: str) -> Optional[dict]:
        """
        Fetches the HTML of a job detail page, determines the parser,
        extracts data, and saves to database.
        """
        logger.info(f"Processing URL in pipeline: {url}")

        try:
            html = await self.crawler.fetch_page_html(url)
        except Exception as e:
            logger.error(f"Failed to fetch HTML for {url}: {e}")
            return None

        if "itviec.com" in url:
            parser: BaseCrawler = ITViecParser(html, url)
        elif "topdev.vn" in url:
            parser = TopDevParser(html, url)
        else:
            logger.error(f"Unsupported site/domain for URL: {url}")
            return None

        try:
            parsed_data = parser.parse()
        except Exception as e:
            logger.error(f"Failed to parse HTML for {url}: {e}")
            return None

        try:
            async with AsyncSessionLocal() as db:
                comp_data = CompanyCreate(**parsed_data["company"])

                existing_company = await CompanyRepository.get_by_name(db, comp_data.name)
                if not existing_company:
                    logger.info(f"Registering new company: {comp_data.name}")
                    company = await CompanyRepository.create(db, comp_data)
                else:
                    logger.info(f"Using existing company: {existing_company.name}")
                    company = existing_company

                job_data_dict = parsed_data["job"]
                job_data_dict["company_id"] = company.id
                job_data = JobCreate(**job_data_dict)

                logger.info(f"Upserting job: {job_data.title}")
                job = await JobService.post_job(db, job_data)

                return {
                    "company_id": company.id,
                    "job_id": job.id,
                    "title": job.title,
                    "url": job.url
                }

        except Exception as e:
            logger.error(f"Failed to save parsed data to DB for {url}: {e}")
            return None
