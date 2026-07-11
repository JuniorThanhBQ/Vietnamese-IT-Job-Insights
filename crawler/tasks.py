# pylint: disable=broad-exception-caught
import asyncio
import sys
import os
from loguru import logger
from crawler.celery_app import celery_app

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from crawler.base.crawler import BaseCrawler
from crawler.pipelines.job_pipeline import JobPipeline
from crawler.parser.itviec_list_parser import ITViecListParser
from crawler.parser.topdev_list_parser import TopDevListParser
from app.modules.jobs.archival_service import ArchivalService


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
)
def process_job_url_task(self, url: str) -> dict:
    """
    Celery task to scrape and process a single job detail page.
    Utilizes exponential backoff for retries.
    """
    logger.info(f"Starting Celery task to process job URL: {url}")

    async def run_pipeline():
        async with BaseCrawler() as crawler:
            pipeline = JobPipeline(crawler=crawler)
            return await pipeline.process_url(url)

    try:
        result = asyncio.run(run_pipeline())
        if result is None:
            logger.warning(f"Processing returned None for job: {url}")
        else:
            logger.info(f"Successfully processed job: {url}")
        return result
    except Exception as exc:
        logger.error(f"Error executing job processing task for {url}: {exc}")
        raise exc


@celery_app.task
def crawl_itviec_list_task(max_pages: int = 5) -> int:
    """
    Celery task to scrape ITviec job lists pagination and queue individual jobs.
    """
    logger.info(f"Starting ITviec list crawling task (max_pages={max_pages})")

    async def run_list_crawl():
        async with BaseCrawler() as crawler:
            page = 1
            total_queued = 0
            while page <= max_pages:
                url = f"https://itviec.com/it-jobs/software-engineer?page={page}"
                logger.info(f"Fetching ITviec list page {page}: {url}")
                try:
                    html = await crawler.fetch_page_html(url)
                except Exception as e:
                    logger.error(f"Failed to fetch ITviec page {page}: {e}")
                    break

                parser = ITViecListParser(html, base_url="https://itviec.com")
                job_urls = parser.parse_job_urls()
                logger.info(f"Found {len(job_urls)} job URLs on page {page}")

                if not job_urls:
                    logger.info("No more job URLs found on ITviec. Stopping list crawl.")
                    break

                for job_url in job_urls:
                    process_job_url_task.delay(job_url)
                    total_queued += 1

                if not parser.has_next_page():
                    logger.info("No next page pagination link found. Stopping list crawl.")
                    break

                page += 1
            return total_queued

    try:
        queued_count = asyncio.run(run_list_crawl())
        logger.info(f"Completed ITviec list crawling. Queued {queued_count} jobs.")
        return queued_count
    except Exception as e:
        logger.error(f"Error during ITviec list crawling task: {e}")
        raise e


@celery_app.task
def crawl_topdev_list_task(max_pages: int = 5) -> int:
    """
    Celery task to scrape TopDev job lists pagination and queue individual jobs.
    """
    logger.info(f"Starting TopDev list crawling task (max_pages={max_pages})")

    async def run_list_crawl():
        async with BaseCrawler() as crawler:
            page = 1
            total_queued = 0
            while page <= max_pages:
                url = f"https://topdev.vn/jobs/search?keyword=Software+Engineer&page={page}"
                logger.info(f"Fetching TopDev list page {page}: {url}")
                try:
                    html = await crawler.fetch_page_html(url)
                except Exception as e:
                    logger.error(f"Failed to fetch TopDev page {page}: {e}")
                    break

                parser = TopDevListParser(html, base_url="https://topdev.vn")
                job_urls = parser.parse_job_urls()
                logger.info(f"Found {len(job_urls)} job URLs on page {page}")

                if not job_urls:
                    logger.info("No more job URLs found on TopDev. Stopping list crawl.")
                    break

                for job_url in job_urls:
                    process_job_url_task.delay(job_url)
                    total_queued += 1

                if not parser.has_next_page():
                    logger.info("No next page pagination link found. Stopping list crawl.")
                    break

                page += 1
            return total_queued

    try:
        queued_count = asyncio.run(run_list_crawl())
        logger.info(f"Completed TopDev list crawling. Queued {queued_count} jobs.")
        return queued_count
    except Exception as e:
        logger.error(f"Error during TopDev list crawling task: {e}")
        raise e


@celery_app.task
def crawl_all_task(max_pages: int = 5) -> str:
    """
    Orchestration task to trigger both ITviec and TopDev list crawls.
    """
    logger.info("Triggering list crawls for all sites")
    crawl_itviec_list_task.delay(max_pages)
    crawl_topdev_list_task.delay(max_pages)
    return "Crawl tasks dispatched"

@celery_app.task(name="archive_stale_jobs_task")
def archive_stale_jobs_task():
    """
    Task lập lịch hàng tuần để nén các job cũ (>90 ngày) ra định dạng Parquet
    và xóa khỏi DB nhằm tối ưu dung lượng PostgreSQL.
    """
    storage_dir = "/app/cold-storage"
    os.makedirs(storage_dir, exist_ok=True)

    # Do ArchivalService là async, chạy bọc qua asyncio
    archived_count = asyncio.run(
        ArchivalService.archive_old_jobs(
            days_old=90,
            storage_dir=storage_dir,
            batch_size=100
        )
    )
    return f"Archived {archived_count} jobs successfully."
