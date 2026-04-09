import enum
from datetime import datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class FeedingFrequency(str, enum.Enum):
    daily = "daily"
    twice_daily = "twice_daily"
    weekly = "weekly"
    custom = "custom"


class FeedingStatus(str, enum.Enum):
    active = "active"
    suspended = "suspended"
    cancelled = "cancelled"


class DailyRationItem(BaseModel):
    item: str
    quantity_g: int
    frequency: str

    @field_validator("quantity_g")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("quantity_g must be greater than 0")
        return v


class DietBase(BaseModel):
    animal_id: UUID
    designed_by: UUID
    name: str
    description: str | None = None
    daily_rations: list[DailyRationItem]
    effective_from: datetime | None = None
    effective_to: datetime | None = None

    @model_validator(mode="after")
    def validate_effective_period(self):
        if (
            self.effective_from
            and self.effective_to
            and self.effective_from >= self.effective_to
        ):
            raise ValueError("effective_from must be before effective_to")
        return self


class DietCreate(DietBase):
    pass


class DietUpdate(BaseModel):
    designed_by: UUID | None = None
    name: str | None = None
    description: str | None = None
    daily_rations: list[DailyRationItem] | None = None
    effective_from: datetime | None = None
    effective_to: datetime | None = None

    @model_validator(mode="after")
    def validate_effective_period(self):
        if (
            self.effective_from
            and self.effective_to
            and self.effective_from >= self.effective_to
        ):
            raise ValueError("effective_from must be before effective_to")
        return self


class DietRead(BaseModel):
    id: UUID
    animal_id: UUID
    designed_by: UUID
    name: str
    description: str | None
    daily_rations: list[DailyRationItem]
    effective_from: datetime
    effective_to: datetime | None
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class FeedingScheduleBase(BaseModel):
    diet_id: UUID
    assigned_to: UUID
    feeding_time: time
    frequency: FeedingFrequency = FeedingFrequency.daily
    instructions: str | None = None
    status: FeedingStatus = FeedingStatus.active


class FeedingScheduleCreate(FeedingScheduleBase):
    pass


class FeedingScheduleUpdate(BaseModel):
    assigned_to: UUID | None = None
    feeding_time: time | None = None
    frequency: FeedingFrequency | None = None
    instructions: str | None = None
    status: FeedingStatus | None = None


class FeedingScheduleRead(FeedingScheduleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
