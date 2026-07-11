import sys
import os
import pytest
from unittest.mock import patch, AsyncMock

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.modules.jobs.analytics_service import AnalyticsService


@pytest.mark.anyio
async def test_analytics_overview_cache_hit():
    """Test that AnalyticsService returns cached overview on Redis cache hit without querying database."""
    fake_payload = {
        "salary_trends": [
            {
                "seniority": "Junior",
                "avg_min_vnd": 10.0,
                "avg_max_vnd": 20.0,
                "job_count": 5,
            }
        ],
        "remote_policies": {"Remote": 5},
        "locations": {"Hồ Chí Minh": 5},
        "tech_stacks": {"Python": 5},
    }

    # Mock get_cache to return payload
    with patch(
        "app.modules.jobs.cache_service.CacheService.get_cache",
        AsyncMock(return_value=fake_payload),
    ) as mock_get_cache:
        # Patch JobRepository methods to make sure they are not called
        with patch(
            "app.modules.jobs.repository.JobRepository.get_salary_trends_by_seniority"
        ) as mock_salaries:
            db_mock = AsyncMock()
            result = await AnalyticsService.get_analytics_overview(db_mock)

            assert result == fake_payload
            mock_get_cache.assert_called_once_with("job_insights:analytics:overview")
            mock_salaries.assert_not_called()


@pytest.mark.anyio
async def test_analytics_overview_cache_miss():
    """Test that AnalyticsService queries database on Redis cache miss, caches results, and returns overview."""
    fake_salaries = [
        {
            "seniority": "Senior",
            "avg_min_vnd": 40.0,
            "avg_max_vnd": 60.0,
            "job_count": 2,
        }
    ]
    fake_remote = {"Hybrid": 10}
    fake_locations = {"Hà Nội": 8}
    fake_tech = {"Golang": 6}

    # Mock get_cache to return None (cache miss) and set_cache to return True
    with patch(
        "app.modules.jobs.cache_service.CacheService.get_cache",
        AsyncMock(return_value=None),
    ) as mock_get_cache, patch(
        "app.modules.jobs.cache_service.CacheService.set_cache",
        AsyncMock(return_value=True),
    ) as mock_set_cache:
        # Mock all database calls in JobRepository
        with patch(
            "app.modules.jobs.repository.JobRepository.get_salary_trends_by_seniority",
            AsyncMock(return_value=fake_salaries),
        ) as mock_sal, patch(
            "app.modules.jobs.repository.JobRepository.get_remote_policy_distribution",
            AsyncMock(return_value=fake_remote),
        ) as mock_rem, patch(
            "app.modules.jobs.repository.JobRepository.get_location_distribution",
            AsyncMock(return_value=fake_locations),
        ) as mock_loc, patch(
            "app.modules.jobs.repository.JobRepository.get_tech_stack_demand",
            AsyncMock(return_value=fake_tech),
        ) as mock_tech:
            db_mock = AsyncMock()
            result = await AnalyticsService.get_analytics_overview(db_mock)

            expected_payload = {
                "salary_trends": fake_salaries,
                "remote_policies": fake_remote,
                "locations": fake_locations,
                "tech_stacks": fake_tech,
            }

            assert result == expected_payload
            mock_get_cache.assert_called_once_with("job_insights:analytics:overview")
            mock_sal.assert_called_once_with(db_mock)
            mock_rem.assert_called_once_with(db_mock)
            mock_loc.assert_called_once_with(db_mock)

            # Check tech stack call keywords
            mock_tech.assert_called_once()
            args, _ = mock_tech.call_args
            assert args[0] == db_mock
            assert "React" in args[1]
            assert "Python" in args[1]

            # Verify set_cache was called with TTL=43200
            mock_set_cache.assert_called_once_with(
                "job_insights:analytics:overview", expected_payload, ttl=43200
            )
