import enum
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator
from uuid import UUID

# enumeraciones
class ConservationStatus(str, enum.Enum):
    extinct = "extinct"
    extinct_in_wild = "extinct_in_wild"
    critically_endangered = "critically_endangered"
    endangered = "endangered"
    vulnerable = "vulnerable"
    near_threatened = "near_threatened"
    least_concern = "least_concern"
    data_deficient = "data_deficient"
    not_evaluated = "not_evaluated"


class DietType(str, enum.Enum):
    herbivore = "herbivore"
    carnivore = "carnivore"
    omnivore = "omnivore"
    insectivore = "insectivore"
    frugivore = "frugivore"


class ClimateType(str, enum.Enum):
    tropical = "tropical"
    arid = "arid"
    temperate = "temperate"
    aquatic = "aquatic"
    polar = "polar"
    subtropical = "subtropical"
    mediterranean = "mediterranean"


class EnclosureType(str, enum.Enum):
    cage = "cage"
    open = "open"
    aquarium = "aquarium"
    aviary = "aviary"
    terrarium = "terrarium"
    mixed = "mixed"


class EnclosureStatus(str, enum.Enum):
    active = "active"
    under_maintenance = "under_maintenance"
    closed = "closed"


class AnimalGender(str, enum.Enum):
    M = "M"
    F = "F"
    unknown = "unknown"


class AnimalStatus(str, enum.Enum):
    active = "active"
    quarantine = "quarantine"
    transferred = "transferred"
    deceased = "deceased"


# esquemas de especies
class SpeciesBase(BaseModel):
    common_name: str
    scientific_name: str
    conservation_status: ConservationStatus = ConservationStatus.data_deficient
    habitat_description: str | None = None
    diet_type: DietType
    additional_info: dict | None = None


class SpeciesCreate(SpeciesBase):
    pass


class SpeciesUpdate(BaseModel):
    common_name: str | None = None
    scientific_name: str | None = None
    conservation_status: ConservationStatus | None = None
    habitat_description: str | None = None
    diet_type: DietType | None = None
    additional_info: dict | None = None


class SpeciesRead(SpeciesBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


# esquemas de zonas
class ZoneBase(BaseModel):
    name: str
    description: str | None = None
    surface_area_m2: float
    climate_type: ClimateType


class ZoneCreate(ZoneBase):
    @field_validator("surface_area_m2")
    @classmethod
    def validate_surface_area(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("surface_area_m2 must be greater than 0")
        return v


class ZoneUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    surface_area_m2: float | None = None
    climate_type: ClimateType | None = None

    @field_validator("surface_area_m2")
    @classmethod
    def validate_surface_area(cls, v: float | None) -> float | None:
        if v is not None and v <= 0:
            raise ValueError("surface_area_m2 must be greater than 0")
        return v


class ZoneRead(ZoneBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


# esquema de pacientes
class EnclosureBase(BaseModel):
    name: str
    zone_id: UUID
    type: EnclosureType
    capacity: int
    area_m2: float
    features: str | None = None
    status: EnclosureStatus = EnclosureStatus.active

    @field_validator("capacity")
    @classmethod
    def validate_capacity(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("capacity must be greater than 0")
        return v

    @field_validator("area_m2")
    @classmethod
    def validate_area(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("area_m2 must be greater than 0")
        return v


class EnclosureCreate(EnclosureBase):
    pass


class EnclosureUpdate(BaseModel):
    name: str | None = None
    zone_id: UUID | None = None
    type: EnclosureType | None = None
    capacity: int | None = None
    area_m2: float | None = None
    features: str | None = None
    status: EnclosureStatus | None = None

    @field_validator("capacity")
    @classmethod
    def validate_capacity(cls, v: int | None) -> int | None:
        if v is not None and v <= 0:
            raise ValueError("capacity must be greater than 0")
        return v

    @field_validator("area_m2")
    @classmethod
    def validate_area(cls, v: float | None) -> float | None:
        if v is not None and v <= 0:
            raise ValueError("area_m2 must be greater than 0")
        return v


class EnclosureRead(EnclosureBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


# esquema de animales
class AnimalBase(BaseModel):
    name: str | None = None
    species_id: UUID
    enclosure_id: UUID
    gender: AnimalGender = AnimalGender.unknown
    birth_date: date | None = None
    arrival_date: date
    origin: str | None = None
    status: AnimalStatus = AnimalStatus.active
    notes: str | None = None

    @field_validator("arrival_date")
    @classmethod
    def validate_arrival_date(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("arrival_date cannot be in the future")
        return v


class AnimalCreate(AnimalBase):
    pass


class AnimalUpdate(BaseModel):
    name: str | None = None
    species_id: UUID | None = None
    enclosure_id: UUID | None = None
    gender: AnimalGender | None = None
    birth_date: date | None = None
    arrival_date: date | None = None
    origin: str | None = None
    status: AnimalStatus | None = None
    notes: str | None = None

    @field_validator("arrival_date")
    @classmethod
    def validate_arrival_date(cls, v: date | None) -> date | None:
        if v is not None and v > date.today():
            raise ValueError("arrival_date cannot be in the future")
        return v


class AnimalRead(AnimalBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class SpeciesSimple(BaseModel):
    id: UUID
    common_name: str
    scientific_name: str
    conservation_status: ConservationStatus

    model_config = ConfigDict(from_attributes=True)


class EnclosureSimple(BaseModel):
    id: UUID
    name: str
    type: EnclosureType
    status: EnclosureStatus

    model_config = ConfigDict(from_attributes=True)


class AnimalWithDetailsRead(AnimalRead):
    species: SpeciesSimple
    enclosure: EnclosureSimple


# esquema de transferencias de animales
class AnimalTransferBase(BaseModel):
    animal_id: UUID
    origin_enclosure_id: UUID
    destination_enclosure_id: UUID
    employee_id: UUID
    transfer_date: datetime
    reason: str | None = None


class AnimalTransferCreate(AnimalTransferBase):
    @field_validator("transfer_date")
    @classmethod
    def validate_transfer_date(cls, v: datetime) -> datetime:
        if v > datetime.now(v.tzinfo):
            raise ValueError("transfer_date cannot be in the future")
        return v


class AnimalTransferRead(AnimalTransferBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
