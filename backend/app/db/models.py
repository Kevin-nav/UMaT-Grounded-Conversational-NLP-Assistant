from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Faculty(Base):
    __tablename__ = "faculties"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    short_name: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    campus: Mapped[str | None] = mapped_column(String(120), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    departments: Mapped[list["Department"]] = relationship(back_populates="faculty")
    staff_members: Mapped[list["StaffMember"]] = relationship(back_populates="faculty")
    location_guides: Mapped[list["LocationGuide"]] = relationship(back_populates="faculty")


class Department(Base):
    __tablename__ = "departments"
    __table_args__ = (UniqueConstraint("faculty_id", "name", name="uq_department_faculty_name"),)

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    faculty_id: Mapped[str | None] = mapped_column(ForeignKey("faculties.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    aliases: Mapped[list[str]] = mapped_column(JSON, default=list)
    campus: Mapped[str | None] = mapped_column(String(120), nullable=True)
    location_guide: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    faculty: Mapped[Faculty | None] = relationship(back_populates="departments")
    staff_members: Mapped[list["StaffMember"]] = relationship(back_populates="department")
    location_guides: Mapped[list["LocationGuide"]] = relationship(back_populates="department")


class StaffMember(Base):
    __tablename__ = "staff_members"

    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), index=True)
    title: Mapped[str | None] = mapped_column(String(80), nullable=True)
    rank_role: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    faculty_id: Mapped[str | None] = mapped_column(ForeignKey("faculties.id"), nullable=True, index=True)
    department_id: Mapped[str | None] = mapped_column(ForeignKey("departments.id"), nullable=True, index=True)
    campus: Mapped[str | None] = mapped_column(String(120), nullable=True)
    specializations: Mapped[list[str]] = mapped_column(JSON, default=list)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    aliases: Mapped[list[str]] = mapped_column(JSON, default=list)
    source_section: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    faculty: Mapped[Faculty | None] = relationship(back_populates="staff_members")
    department: Mapped[Department | None] = relationship(back_populates="staff_members")


class LocationGuide(Base):
    __tablename__ = "location_guides"

    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    faculty_id: Mapped[str | None] = mapped_column(ForeignKey("faculties.id"), nullable=True, index=True)
    department_id: Mapped[str | None] = mapped_column(ForeignKey("departments.id"), nullable=True, index=True)
    campus: Mapped[str | None] = mapped_column(String(120), nullable=True)
    directions_text: Mapped[str] = mapped_column(Text)

    faculty: Mapped[Faculty | None] = relationship(back_populates="location_guides")
    department: Mapped[Department | None] = relationship(back_populates="location_guides")


class AdminUser(Base):
    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class QueryLog(Base):
    __tablename__ = "query_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    query_text: Mapped[str] = mapped_column(Text)
    intent: Mapped[str | None] = mapped_column(String(64), nullable=True)
    confidence: Mapped[str | None] = mapped_column(String(32), nullable=True)
    matched_entity_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
