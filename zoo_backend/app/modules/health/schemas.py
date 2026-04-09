import enum
from datetime import datetime, timedelta, timezone
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

# esquemas de registro medico
class UrgencyLevel(str, enum.Enum):
    low = "low"
    normal = "normal"
    urgent = "urgent"
    critical = "critical"


class MedicalRecordBase(BaseModel):
    animal_id: UUID
    performed_by: UUID
    visit_date: datetime
    diagnosis: str | None = None
    treatment: str | None = None
    observations: str | None = None
    urgency_level: UrgencyLevel = UrgencyLevel.normal

    @field_validator("visit_date")
    @classmethod
    def validate_visit_date(cls, v: datetime) -> datetime:
        now = datetime.now(timezone.utc)
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v > now:
            raise ValueError("visit_date cannot be in the future")
        return v


class MedicalRecordCreate(MedicalRecordBase):
    pass


class MedicalRecordUpdate(BaseModel):
    visit_date: datetime | None = None
    diagnosis: str | None = None
    treatment: str | None = None
    observations: str | None = None
    urgency_level: UrgencyLevel | None = None

    @field_validator("visit_date")
    @classmethod
    def validate_visit_date(cls, v: datetime | None) -> datetime | None:
        if v is None:
            return v
        now = datetime.now(timezone.utc)
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v > now:
            raise ValueError("visit_date cannot be in the future")
        return v


class MedicalRecordRead(MedicalRecordBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)

# esquemas de vacunas
class VaccineBase(BaseModel):
    name: str
    description: str | None = None
    validity_period: timedelta | None = None


class VaccineCreate(VaccineBase):
    pass


class VaccineUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    validity_period: timedelta | None = None


class VaccineRead(VaccineBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)

# esquemas de vacunacion
class MedicalVaccinationBase(BaseModel):
    medical_record_id: UUID
    vaccine_id: UUID
    application_date: datetime
    next_due_date: datetime | None = None
    batch_number: str | None = None
    notes: str | None = None

    @field_validator("application_date")
    @classmethod
    def validate_application_date(cls, v: datetime) -> datetime:
        now = datetime.now(timezone.utc)
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v > now:
            raise ValueError("application_date cannot be in the future")
        return v


class MedicalVaccinationCreate(MedicalVaccinationBase):
    pass


class MedicalVaccinationUpdate(BaseModel):
    application_date: datetime | None = None
    next_due_date: datetime | None = None
    batch_number: str | None = None
    notes: str | None = None

    @field_validator("application_date")
    @classmethod
    def validate_application_date(cls, v: datetime | None) -> datetime | None:
        if v is None:
            return v
        now = datetime.now(timezone.utc)
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v > now:
            raise ValueError("application_date cannot be in the future")
        return v


class MedicalVaccinationRead(MedicalVaccinationBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
