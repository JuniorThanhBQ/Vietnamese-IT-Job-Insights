from datetime import datetime
from enum import Enum
from uuid import UUID
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class SalaryCurrency(str, Enum):
    VND = "VND"
    USD = "USD"


class Seniority(str, Enum):
    Intern = "Intern"
    Fresher = "Fresher"
    Junior = "Junior"
    Middle = "Middle"
    Senior = "Senior"
    Lead = "Lead"
    Manager = "Manager"
    Unknown = "Unknown"


class RemotePolicy(str, Enum):
    Remote = "Remote"
    Hybrid = "Hybrid"
    Onsite = "Onsite"
    Unknown = "Unknown"


class EmploymentType(str, Enum):
    Full_time = "Full-time"
    Part_time = "Part-time"
    Contract = "Contract"
    Internship = "Internship"
    Unknown = "Unknown"


class JobBase(BaseModel):
    title: str
    source_id: str
    source_site: str
    url: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[SalaryCurrency] = SalaryCurrency.VND
    salary_raw: Optional[str] = None
    seniority: Optional[Seniority] = Seniority.Unknown
    remote_policy: Optional[RemotePolicy] = RemotePolicy.Unknown
    employment_type: Optional[EmploymentType] = EmploymentType.Unknown
    description: str
    requirements: Optional[str] = None
    posting_time: Optional[datetime] = None
    expiry_time: Optional[datetime] = None
    raw_metadata: Optional[Dict[str, Any]] = None
    is_active: bool = True
    content_hash: str


class JobCreate(JobBase):
    company_id: UUID


class JobResponse(JobBase):
    id: UUID
    company_id: UUID
    created_date: datetime
    updated_date: datetime

    model_config = ConfigDict(from_attributes=True)


class JobFilterParams(BaseModel):
    title: Optional[str] = None
    seniority: Optional[Seniority] = None
    remote_policy: Optional[RemotePolicy] = None
    employment_type: Optional[EmploymentType] = None
    min_salary: Optional[float] = None


class JobSemanticSearchResponse(BaseModel):
    job: JobResponse
    similarity_score: float


class ChatMessage(BaseModel):
    role: str  # "user" | "model"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[list[ChatMessage]] = None
