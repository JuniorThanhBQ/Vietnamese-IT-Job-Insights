import sys
import os
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.modules.jobs.archival_service import ArchivalService
from app.models.db_models import Job, Company


@pytest.mark.anyio
async def test_archive_old_jobs_success(tmp_path):
    """Test that ArchivalService correctly fetches, serializes to parquet, and deletes old jobs."""
    # Setup mock jobs
    mock_company = Company(name="Test Company", address="Test Address")
    mock_job = Job(
        id="e60d2979-5487-4d6d-b8d1-7299a9a3b680",
        source_id="123",
        source_site="itviec",
        title="Software Engineer",
        url="http://example.com",
        salary_min=10000000.0,
        salary_max=20000000.0,
        salary_currency="VND",
        salary_raw="10M - 20M VND",
        seniority="Junior",
        remote_policy="Remote",
        employment_type="Full-time",
        description="Job Description",
        requirements="Job Requirements",
        company=mock_company,
    )

    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    # Mock session.execute for selecting jobs
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_job]
    mock_session.execute.return_value = mock_result

    # Mock AsyncSessionLocal context manager
    with patch(
        "app.modules.jobs.archival_service.AsyncSessionLocal", return_value=mock_session
    ):
        storage_dir = str(tmp_path)
        archived_count = await ArchivalService.archive_old_jobs(
            days_old=90, storage_dir=storage_dir, batch_size=10
        )

        assert archived_count == 1

        # Verify Parquet file was created in tmp_path
        files = os.listdir(storage_dir)
        assert len(files) == 1
        assert files[0].endswith(".parquet")

        # Verify SQL delete statement was called
        assert mock_session.execute.call_count == 2  # 1 for select, 1 for delete
        mock_session.commit.assert_called_once()


@pytest.mark.anyio
async def test_archive_old_jobs_no_stale_jobs(tmp_path):
    """Test that ArchivalService returns 0 and does not write parquet if no matching jobs found."""
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    with patch(
        "app.modules.jobs.archival_service.AsyncSessionLocal", return_value=mock_session
    ):
        storage_dir = str(tmp_path)
        archived_count = await ArchivalService.archive_old_jobs(
            days_old=90, storage_dir=storage_dir, batch_size=10
        )

        assert archived_count == 0
        assert len(os.listdir(storage_dir)) == 0
        mock_session.commit.assert_not_called()
