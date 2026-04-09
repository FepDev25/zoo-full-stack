import uuid
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, ForeignKey, DateTime, Date, Float, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.modules.personnel.models import Employee

# modelo de espcies
class Species(Base):
    __tablename__ = "species"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    common_name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    scientific_name: Mapped[str] = mapped_column(
        String(150), unique=True, nullable=False
    )
    conservation_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="data_deficient"
    )
    habitat_description: Mapped[str | None] = mapped_column(Text)
    diet_type: Mapped[str] = mapped_column(String(100), nullable=False)
    additional_info: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    animals: Mapped[list["Animal"]] = relationship(
        "Animal", back_populates="species", lazy="selectin"
    )

# modelo de zonas
class Zone(Base):
    __tablename__ = "zones"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    surface_area_m2: Mapped[float] = mapped_column(Float, nullable=False)
    climate_type: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    enclosures: Mapped[list["Enclosure"]] = relationship(
        "Enclosure", back_populates="zone", lazy="selectin"
    )

# modelo de recintos
class Enclosure(Base):
    __tablename__ = "enclosures"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    zone_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("zones.id", ondelete="RESTRICT"),
        nullable=False,
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    area_m2: Mapped[float] = mapped_column(Float, nullable=False)
    features: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    zone: Mapped["Zone"] = relationship(
        "Zone", back_populates="enclosures", lazy="selectin"
    )
    animals: Mapped[list["Animal"]] = relationship(
        "Animal", back_populates="enclosure", lazy="selectin"
    )

# modelo de animales
class Animal(Base):
    __tablename__ = "animals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str | None] = mapped_column(String(100))
    species_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("species.id", ondelete="RESTRICT"),
        nullable=False,
    )
    enclosure_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enclosures.id", ondelete="RESTRICT"),
        nullable=False,
    )
    gender: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
    birth_date: Mapped[date | None] = mapped_column(Date)
    arrival_date: Mapped[date] = mapped_column(Date, nullable=False)
    origin: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    species: Mapped["Species"] = relationship(
        "Species", back_populates="animals", lazy="selectin"
    )
    enclosure: Mapped["Enclosure"] = relationship(
        "Enclosure", back_populates="animals", lazy="selectin"
    )
    transfers: Mapped[list["AnimalTransfer"]] = relationship(
        "AnimalTransfer", back_populates="animal", lazy="selectin"
    )

# modelo de transferencia de animales
class AnimalTransfer(Base):
    __tablename__ = "animal_transfers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    animal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("animals.id", ondelete="RESTRICT"),
        nullable=False,
    )
    origin_enclosure_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enclosures.id", ondelete="RESTRICT"),
        nullable=False,
    )
    destination_enclosure_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enclosures.id", ondelete="RESTRICT"),
        nullable=False,
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
    )
    transfer_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    reason: Mapped[str | None] = mapped_column(Text)

    animal: Mapped["Animal"] = relationship(
        "Animal", back_populates="transfers", lazy="selectin"
    )
    origin_enclosure: Mapped["Enclosure"] = relationship(
        "Enclosure", foreign_keys=[origin_enclosure_id], lazy="selectin"
    )
    destination_enclosure: Mapped["Enclosure"] = relationship(
        "Enclosure", foreign_keys=[destination_enclosure_id], lazy="selectin"
    )
    employee: Mapped["Employee"] = relationship("Employee", lazy="selectin")
