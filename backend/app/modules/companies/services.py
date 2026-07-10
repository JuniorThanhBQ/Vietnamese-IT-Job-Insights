from uuid import UUID
from typing import Sequence
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db_models import Company
from app.modules.companies.models import CompanyCreate
from app.modules.companies.repository import CompanyRepository


class CompanyService:
    """Service layer coordinating business logic for companies."""

    @staticmethod
    async def get_company(db: AsyncSession, company_id: UUID) -> Company:
        """Retrieve a company by ID or raise 404."""
        company = await CompanyRepository.get_by_id(db, company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with ID {company_id} not found",
            )
        return company

    @staticmethod
    async def list_companies(
        db: AsyncSession, limit: int = 100, offset: int = 0
    ) -> Sequence[Company]:
        """Retrieve list of companies."""
        return await CompanyRepository.list_all(db, limit, offset)

    @staticmethod
    async def register_company(db: AsyncSession, company_in: CompanyCreate) -> Company:
        """Register a new company, ensuring name uniqueness."""
        existing_company = await CompanyRepository.get_by_name(db, company_in.name)
        if existing_company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Company name '{company_in.name}' is already registered.",
            )
        return await CompanyRepository.create(db, company_in)
