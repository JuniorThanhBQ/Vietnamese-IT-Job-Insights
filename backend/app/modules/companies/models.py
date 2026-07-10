from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class CompanyBase(BaseModel):
    name: str
    source_id: str
    source_site: str
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    address: Optional[str] = None
    raw_metadata: Optional[Dict[str, Any]] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    id: UUID
    created_date: datetime
    updated_date: datetime

    model_config = ConfigDict(from_attributes=True)
