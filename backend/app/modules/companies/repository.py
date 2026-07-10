from uuid import UUID
from typing import Sequence, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db_models import Company
from app.modules.companies.models import CompanyCreate


class CompanyRepository:
    """Repository pattern for database operations on Company objects."""

    @staticmethod
    async def get_by_id(db: AsyncSession, company_id: UUID) -> Optional[Company]:
        """Fetch a company by its primary key ID."""
        result = await db.execute(select(Company).where(Company.id == company_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[Company]:
        """Fetch a company by name (unique constraint check)."""
        result = await db.execute(select(Company).where(Company.name == name))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_all(
        db: AsyncSession, limit: int = 100, offset: int = 0
    ) -> Sequence[Company]:
        """List companies with pagination."""
        result = await db.execute(select(Company).offset(offset).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, company_in: CompanyCreate) -> Company:
        """Create a new company in the database."""
        db_company = Company(
            source_id=company_in.source_id,
            source_site=company_in.source_site,
            name=company_in.name,
            logo_url=company_in.logo_url,
            website_url=company_in.website_url,
            company_size=company_in.company_size,
            industry=company_in.industry,
            address=company_in.address,
            raw_metadata=company_in.raw_metadata or {},
        )
        db.add(db_company)
        await db.commit()
        await db.refresh(db_company)
        return db_company
