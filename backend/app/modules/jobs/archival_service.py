import os
from datetime import datetime, timedelta, timezone
from loguru import logger
import pyarrow as pa
import pyarrow.parquet as pq
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload
from app.models.db_models import Job
from app.models.database import AsyncSessionLocal


class ArchivalService:
    @staticmethod
    async def archive_old_jobs(
        days_old: int = 90,
        storage_dir: str = "/app/cold-storage",
        batch_size: int = 1000,
    ) -> int:
        """
        Query jobs older than `days_old` days, serialize them to a compressed
        Parquet file, delete them from the active PostgreSQL database, and return
        the count of successfully archived jobs.
        """
        # cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        cutoff_date = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
            days=days_old
        )
        logger.info(
            f"Starting database archival for jobs created before {cutoff_date.isoformat()} (Older than {days_old} days)"
        )

        # 1. Fetch old jobs in batches to keep memory usage low
        async with AsyncSessionLocal() as session:
            stmt = (
                select(Job)
                .options(joinedload(Job.company))
                .where(Job.created_date < cutoff_date)
                .limit(batch_size)
            )
            result = await session.execute(stmt)
            jobs = result.scalars().all()

            if not jobs:
                logger.info("No stale jobs found matching the archival criteria.")
                return 0

            logger.info(f"Found {len(jobs)} jobs to archive in this batch.")

            # 2. Serialize database records into pyarrow compatible structure
            job_dicts = []
            job_ids = []
            for job in jobs:
                job_ids.append(job.id)
                job_dicts.append(
                    {
                        "id": str(job.id),
                        "company_name": job.company.name if job.company else None,
                        "company_address": job.company.address if job.company else None,
                        "source_id": job.source_id,
                        "source_site": job.source_site,
                        "title": job.title,
                        "url": job.url,
                        "salary_min": float(job.salary_min)
                        if job.salary_min is not None
                        else None,
                        "salary_max": float(job.salary_max)
                        if job.salary_max is not None
                        else None,
                        "salary_currency": job.salary_currency,
                        "salary_raw": job.salary_raw,
                        "seniority": job.seniority,
                        "remote_policy": job.remote_policy,
                        "employment_type": job.employment_type,
                        "description": job.description,
                        "requirements": job.requirements,
                        "posting_time": job.posting_time.isoformat()
                        if job.posting_time
                        else None,
                        "expiry_time": job.expiry_time.isoformat()
                        if job.expiry_time
                        else None,
                        "created_date": job.created_date.isoformat()
                        if job.created_date
                        else None,
                    }
                )

            # 3. Write to compressed Parquet file inside storage volume
            try:
                os.makedirs(storage_dir, exist_ok=True)
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                filename = f"jobs_archive_{timestamp}.parquet"
                file_path = os.path.join(storage_dir, filename)

                # Schema definition for pyarrow table
                schema = pa.schema(
                    [
                        ("id", pa.string()),
                        ("company_name", pa.string()),
                        ("company_address", pa.string()),
                        ("source_id", pa.string()),
                        ("source_site", pa.string()),
                        ("title", pa.string()),
                        ("url", pa.string()),
                        ("salary_min", pa.float64()),
                        ("salary_max", pa.float64()),
                        ("salary_currency", pa.string()),
                        ("salary_raw", pa.string()),
                        ("seniority", pa.string()),
                        ("remote_policy", pa.string()),
                        ("employment_type", pa.string()),
                        ("description", pa.string()),
                        ("requirements", pa.string()),
                        ("posting_time", pa.string()),
                        ("expiry_time", pa.string()),
                        ("created_date", pa.string()),
                    ]
                )

                table = pa.Table.from_pydict(
                    {key: [d[key] for d in job_dicts] for key in schema.names},
                    schema=schema,
                )

                # Save compressed Snappy parquet
                pq.write_table(table, file_path, compression="snappy")
                logger.info(f"Successfully archived batch to {file_path}")

            except Exception as e:
                logger.error(f"Failed to write Parquet archival file: {str(e)}")
                raise e

            # 4. Safely delete the archived records from the active database
            try:
                delete_stmt = delete(Job).where(Job.id.in_(job_ids))
                await session.execute(delete_stmt)
                await session.commit()
                logger.info(
                    f"Successfully deleted {len(job_ids)} archived jobs from PostgreSQL."
                )
                return len(job_ids)
            except Exception as e:
                await session.rollback()
                logger.error(
                    f"Failed to delete archived jobs from PostgreSQL, rolling back: {str(e)}"
                )
                # If deletion fails, delete the written Parquet file to avoid duplication in future runs
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise e
