import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
    Numeric,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector


class Base(DeclarativeBase):
    pass


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_id: Mapped[str] = mapped_column(String(255), nullable=False)
    source_site: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # "itviec" | "topdev"
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    logo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    company_size: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Store raw scraped metadata about the company
    raw_metadata: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")

    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 1-to-many relationship with Job
    jobs: Mapped[List["Job"]] = relationship(
        "Job", back_populates="company", cascade="all, delete-orphan"
    )


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )

    source_id: Mapped[str] = mapped_column(String(255), nullable=False)
    source_site: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # "itviec" | "topdev"
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    salary_min: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    salary_max: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    salary_currency: Mapped[Optional[str]] = mapped_column(
        String(10),
        CheckConstraint("salary_currency IN ('VND', 'USD')"),
        default="VND",
        server_default="VND",
    )
    salary_raw: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    seniority: Mapped[Optional[str]] = mapped_column(
        String(100),
        CheckConstraint(
            "seniority IN ('Intern', 'Fresher', 'Junior', 'Middle', 'Senior', 'Lead', 'Manager', 'Unknown')"
        ),
        default="Unknown",
        server_default="Unknown",
    )
    remote_policy: Mapped[Optional[str]] = mapped_column(
        String(50),
        CheckConstraint("remote_policy IN ('Remote', 'Hybrid', 'Onsite', 'Unknown')"),
        default="Unknown",
        server_default="Unknown",
    )
    employment_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        CheckConstraint(
            "employment_type IN ('Full-time', 'Part-time', 'Contract', 'Internship', 'Unknown')"
        ),
        default="Unknown",
        server_default="Unknown",
    )

    description: Mapped[str] = mapped_column(Text, nullable=False)
    requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    posting_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expiry_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Store secondary arrays: skills, benefits, detailed locations
    raw_metadata: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true"
    )
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="jobs")
    embedding_relation: Mapped[Optional["JobEmbedding"]] = relationship(
        "JobEmbedding", back_populates="job", cascade="all, delete-orphan"
    )


class JobEmbedding(Base):
    __tablename__ = "job_embeddings"

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True
    )

    # Gemini Embedding-001 has 768 dimensions
    embedding: Mapped[Vector] = mapped_column(Vector(768), nullable=False)

    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationship
    job: Mapped["Job"] = relationship("Job", back_populates="embedding_relation")
