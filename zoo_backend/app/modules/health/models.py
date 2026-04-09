import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, INTERVAL
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# modelo de registro medico
class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    animal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("animals.id", ondelete="RESTRICT"),
        nullable=False,
    )
    performed_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
    )
    visit_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    diagnosis: Mapped[str | None] = mapped_column(String(100))
    treatment: Mapped[str | None] = mapped_column(Text)
    observations: Mapped[str | None] = mapped_column(Text)
    urgency_level: Mapped[str] = mapped_column(
        String(50), nullable=False, default="normal"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    animal = relationship("Animal", lazy="selectin")
    performer = relationship("Employee", lazy="selectin")
    vaccinations: Mapped[list["MedicalVaccination"]] = relationship(
        "MedicalVaccination", back_populates="medical_record", lazy="selectin"
    )

# modelo de vacuna
class Vaccine(Base):
    __tablename__ = "vaccines"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    validity_period: Mapped[timedelta | None] = mapped_column(INTERVAL)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    vaccinations: Mapped[list["MedicalVaccination"]] = relationship(
        "MedicalVaccination", back_populates="vaccine", lazy="selectin"
    )

# modelo de vacunacion
class MedicalVaccination(Base):
    __tablename__ = "medical_vaccinations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    medical_record_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("medical_records.id", ondelete="CASCADE"),
        nullable=False,
    )
    vaccine_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vaccines.id", ondelete="RESTRICT"),
        nullable=False,
    )
    application_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    next_due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    batch_number: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)

    medical_record: Mapped[MedicalRecord] = relationship(
        "MedicalRecord", back_populates="vaccinations", lazy="selectin"
    )
    vaccine: Mapped[Vaccine] = relationship(
        "Vaccine", back_populates="vaccinations", lazy="selectin"
    )
