from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.companies.models import CompanyCreate, CompanyResponse
from app.modules.companies.services import CompanyService


class CompanyViews:
    """Views layer handling payload transformations and invoking business services."""

    @staticmethod
    async def get_company(db: AsyncSession, company_id: UUID) -> CompanyResponse:
        """Fetch a single company and return it as a serialized response schema."""
        db_company = await CompanyService.get_company(db, company_id)
        return CompanyResponse.model_validate(db_company)

    @staticmethod
    async def list_companies(
        db: AsyncSession, limit: int, offset: int
    ) -> List[CompanyResponse]:
        """Fetch list of companies and return them as a list of response schemas."""
        companies = await CompanyService.list_companies(db, limit, offset)
        return [CompanyResponse.model_validate(c) for c in companies]

    @staticmethod
    async def create_company(
        db: AsyncSession, company_in: CompanyCreate
    ) -> CompanyResponse:
        """Create a company and return its serialized representation."""
        db_company = await CompanyService.register_company(db, company_in)
        return CompanyResponse.model_validate(db_company)
