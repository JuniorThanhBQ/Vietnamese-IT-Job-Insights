from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.modules.companies.models import CompanyCreate, CompanyResponse
from app.modules.companies.views import CompanyViews

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/", response_model=List[CompanyResponse])
async def list_companies(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a list of companies with optional pagination limits."""
    return await CompanyViews.list_companies(db, limit=limit, offset=offset)


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: UUID, db: AsyncSession = Depends(get_db)):
    """Retrieve a specific company profile by its UUID."""
    return await CompanyViews.get_company(db, company_id)


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(company_in: CompanyCreate, db: AsyncSession = Depends(get_db)):
    """Register a new company profile."""
    return await CompanyViews.create_company(db, company_in)
