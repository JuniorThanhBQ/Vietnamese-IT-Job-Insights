"""
Service layer managing IT recruitment market trend statistics and dashboard metrics.
Integrates Redis caching to prevent database load on frequent dashboard queries.
"""

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.jobs.repository import JobRepository
from app.modules.jobs.cache_service import CacheService

# Standard tech stack keywords to monitor in job descriptions
ANALYTICS_KEYWORDS = [
    "React",
    "Angular",
    "Vue",
    "TypeScript",
    "Next.js",
    "Python",
    "Golang",
    "Node.js",
    "Java",
    "PHP",
    "Docker",
    "Kubernetes",
    "AWS",
]


# pylint: disable=too-few-public-methods
class AnalyticsService:
    """Service layer managing IT job market trend statistics with Redis caching."""

    @staticmethod
    async def get_analytics_overview(db: AsyncSession) -> dict:
        """
        Get aggregated IT job trends.
        Checks Redis cache first, falls back to PostgreSQL on cache miss.
        """
        cache_key = "job_insights:analytics:overview"

        # Step 1: Check Redis cache
        cached_data = await CacheService.get_cache(cache_key)
        if cached_data is not None:
            return cached_data

        # Step 2: Cache miss - run database queries sequentially to prevent Session conflicts
        logger.info("Cache miss for analytics overview. Querying database...")
        try:
            salaries = await JobRepository.get_salary_trends_by_seniority(db)
            remote_policies = await JobRepository.get_remote_policy_distribution(db)
            locations = await JobRepository.get_location_distribution(db)
            tech_stacks = await JobRepository.get_tech_stack_demand(
                db, ANALYTICS_KEYWORDS
            )

            payload = {
                "salary_trends": salaries,
                "remote_policies": remote_policies,
                "locations": locations,
                "tech_stacks": tech_stacks,
            }

            # Step 3: Write payload back to Redis cache (TTL = 12 hours)
            await CacheService.set_cache(cache_key, payload, ttl=43200)
            return payload

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Failed to calculate analytics overview from DB: {e}")
            raise e
