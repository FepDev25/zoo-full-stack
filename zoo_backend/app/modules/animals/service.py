from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.exceptions import (
    ConflictException,
    NotFoundException,
    ValidationException,
)
from app.modules.animals.models import Animal, AnimalTransfer, Enclosure, Species, Zone
from app.modules.animals.repository import (
    AnimalRepository,
    AnimalTransferRepository,
    EnclosureRepository,
    SpeciesRepository,
    ZoneRepository,
)
from app.modules.animals.schemas import (
    AnimalCreate,
    AnimalTransferCreate,
    AnimalUpdate,
    EnclosureCreate,
    EnclosureUpdate,
    SpeciesCreate,
    SpeciesUpdate,
    ZoneCreate,
    ZoneUpdate,
)
from app.modules.personnel.repository import EmployeeRepository

# serrvicio de especies
class SpeciesService:
    def __init__(self, repo: SpeciesRepository):
        self.repo = repo

    async def list_all(self, skip: int = 0, limit: int = 20) -> list[Species]:
        return await self.repo.list(skip=skip, limit=limit)

    async def get_by_id(self, species_id: UUID) -> Species:
        species = await self.repo.get_by_id(species_id)
        if not species:
            raise NotFoundException("Species not found")
        return species

    async def create(self, data: SpeciesCreate) -> Species:
        existing = await self.repo.get_by_common_name(data.common_name)
        if existing:
            raise ConflictException(
                f"Species with common name '{data.common_name}' already exists"
            )
        existing = await self.repo.get_by_scientific_name(data.scientific_name)
        if existing:
            raise ConflictException(
                f"Species with scientific name '{data.scientific_name}' already exists"
            )
        species = Species(
            common_name=data.common_name,
            scientific_name=data.scientific_name,
            conservation_status=data.conservation_status.value,
            habitat_description=data.habitat_description,
            diet_type=data.diet_type.value,
            additional_info=data.additional_info,
        )
        try:
            return await self.repo.create(species)
        except IntegrityError:
            raise ConflictException("Species creation failed due to a conflict")

    async def update(self, species_id: UUID, data: SpeciesUpdate) -> Species:
        species = await self.get_by_id(species_id)
        if data.common_name is not None:
            existing = await self.repo.get_by_common_name(data.common_name)
            if existing and existing.id != species_id:
                raise ConflictException(
                    f"Species with common name '{data.common_name}' already exists"
                )
            species.common_name = data.common_name
        if data.scientific_name is not None:
            existing = await self.repo.get_by_scientific_name(data.scientific_name)
            if existing and existing.id != species_id:
                raise ConflictException(
                    f"Species with scientific name '{data.scientific_name}' already exists"
                )
            species.scientific_name = data.scientific_name
        if data.conservation_status is not None:
            species.conservation_status = data.conservation_status.value
        if data.habitat_description is not None:
            species.habitat_description = data.habitat_description
        if data.diet_type is not None:
            species.diet_type = data.diet_type.value
        if data.additional_info is not None:
            species.additional_info = data.additional_info
        try:
            return await self.repo.update(species)
        except IntegrityError:
            raise ConflictException("Species update failed due to a conflict")

    async def delete(self, species_id: UUID) -> None:
        await self.get_by_id(species_id)
        await self.repo.delete(species_id)

# servicio de zonas
class ZoneService:
    def __init__(self, repo: ZoneRepository, enclosure_repo: EnclosureRepository):
        self.repo = repo
        self.enclosure_repo = enclosure_repo

    async def list_all(self, skip: int = 0, limit: int = 20) -> list[Zone]:
        return await self.repo.list(skip=skip, limit=limit)

    async def get_by_id(self, zone_id: UUID) -> Zone:
        zone = await self.repo.get_by_id(zone_id)
        if not zone:
            raise NotFoundException("Zone not found")
        return zone

    async def create(self, data: ZoneCreate) -> Zone:
        existing = await self.repo.get_by_name(data.name)
        if existing:
            raise ConflictException(f"Zone with name '{data.name}' already exists")
        zone = Zone(
            name=data.name,
            description=data.description,
            surface_area_m2=data.surface_area_m2,
            climate_type=data.climate_type.value,
        )
        try:
            return await self.repo.create(zone)
        except IntegrityError:
            raise ConflictException("Zone creation failed due to a conflict")

    async def update(self, zone_id: UUID, data: ZoneUpdate) -> Zone:
        zone = await self.get_by_id(zone_id)
        if data.name is not None:
            existing = await self.repo.get_by_name(data.name)
            if existing and existing.id != zone_id:
                raise ConflictException(f"Zone with name '{data.name}' already exists")
            zone.name = data.name
        if data.description is not None:
            zone.description = data.description
        if data.surface_area_m2 is not None:
            zone.surface_area_m2 = data.surface_area_m2
        if data.climate_type is not None:
            zone.climate_type = data.climate_type.value
        try:
            return await self.repo.update(zone)
        except IntegrityError:
            raise ConflictException("Zone update failed due to a conflict")

    async def delete(self, zone_id: UUID) -> None:
        await self.get_by_id(zone_id)
        if await self.repo.has_enclosures(zone_id):
            raise ValidationException(
                "Cannot delete zone: enclosures are assigned to it"
            )
        await self.repo.delete(zone_id)

# servicio de recintos
class EnclosureService:
    def __init__(self, repo: EnclosureRepository, animal_repo: AnimalRepository):
        self.repo = repo
        self.animal_repo = animal_repo

    async def list_all(self, skip: int = 0, limit: int = 20) -> list[Enclosure]:
        return await self.repo.list(skip=skip, limit=limit)

    async def get_by_id(self, enclosure_id: UUID) -> Enclosure:
        enclosure = await self.repo.get_by_id(enclosure_id)
        if not enclosure:
            raise NotFoundException("Enclosure not found")
        return enclosure

    async def create(self, data: EnclosureCreate) -> Enclosure:
        enclosure = Enclosure(
            name=data.name,
            zone_id=data.zone_id,
            type=data.type.value,
            capacity=data.capacity,
            area_m2=data.area_m2,
            features=data.features,
            status=data.status.value,
        )
        try:
            return await self.repo.create(enclosure)
        except IntegrityError:
            raise ConflictException("Enclosure creation failed due to a conflict")

    async def update(self, enclosure_id: UUID, data: EnclosureUpdate) -> Enclosure:
        enclosure = await self.get_by_id(enclosure_id)
        if data.name is not None:
            enclosure.name = data.name
        if data.zone_id is not None:
            enclosure.zone_id = data.zone_id
        if data.type is not None:
            enclosure.type = data.type.value
        if data.capacity is not None:
            enclosure.capacity = data.capacity
        if data.area_m2 is not None:
            enclosure.area_m2 = data.area_m2
        if data.features is not None:
            enclosure.features = data.features
        if data.status is not None:
            enclosure.status = data.status.value
        try:
            return await self.repo.update(enclosure)
        except IntegrityError:
            raise ConflictException("Enclosure update failed due to a conflict")

    async def delete(self, enclosure_id: UUID) -> None:
        await self.get_by_id(enclosure_id)
        active_count = await self.repo.count_animals(enclosure_id)
        if active_count > 0:
            raise ValidationException(
                f"Cannot delete enclosure: {active_count} active animal(s) are assigned"
            )
        await self.repo.delete(enclosure_id)

# servicio de animales
class AnimalService:
    def __init__(
        self,
        repo: AnimalRepository,
        species_repo: SpeciesRepository,
        enclosure_repo: EnclosureRepository,
        transfer_repo: AnimalTransferRepository,
    ):
        self.repo = repo
        self.species_repo = species_repo
        self.enclosure_repo = enclosure_repo
        self.transfer_repo = transfer_repo

    async def list_all(self, skip: int = 0, limit: int = 20) -> list[Animal]:
        return await self.repo.list_active(skip=skip, limit=limit)

    async def get_by_id(self, animal_id: UUID) -> Animal:
        animal = await self.repo.get_by_id(animal_id)
        if not animal:
            raise NotFoundException("Animal not found")
        return animal

    async def create(self, data: AnimalCreate) -> Animal:
        # Validate species exists
        species = await self.species_repo.get_by_id(data.species_id)
        if not species:
            raise NotFoundException("Species not found")

        # Validate enclosure exists and is active
        enclosure = await self.enclosure_repo.get_by_id(data.enclosure_id)
        if not enclosure:
            raise NotFoundException("Enclosure not found")
        if enclosure.status not in ("active",):
            raise ValidationException("Cannot assign animal to an inactive enclosure")

        animal = Animal(
            name=data.name,
            species_id=data.species_id,
            enclosure_id=data.enclosure_id,
            gender=data.gender.value,
            birth_date=data.birth_date,
            arrival_date=data.arrival_date,
            origin=data.origin,
            status=data.status.value,
            notes=data.notes,
        )
        try:
            return await self.repo.create(animal)
        except IntegrityError:
            raise ConflictException("Animal creation failed due to a conflict")

    async def update(self, animal_id: UUID, data: AnimalUpdate) -> Animal:
        animal = await self.get_by_id(animal_id)

        if data.species_id is not None:
            species = await self.species_repo.get_by_id(data.species_id)
            if not species:
                raise NotFoundException("Species not found")
            animal.species_id = data.species_id

        if data.enclosure_id is not None:
            enclosure = await self.enclosure_repo.get_by_id(data.enclosure_id)
            if not enclosure:
                raise NotFoundException("Enclosure not found")
            if enclosure.status not in ("active",):
                raise ValidationException("Cannot move animal to an inactive enclosure")
            animal.enclosure_id = data.enclosure_id

        if data.name is not None:
            animal.name = data.name
        if data.gender is not None:
            animal.gender = data.gender.value
        if data.birth_date is not None:
            animal.birth_date = data.birth_date
        if data.arrival_date is not None:
            animal.arrival_date = data.arrival_date
        if data.origin is not None:
            animal.origin = data.origin
        if data.status is not None:
            animal.status = data.status.value
        if data.notes is not None:
            animal.notes = data.notes

        try:
            return await self.repo.update(animal)
        except IntegrityError:
            raise ConflictException("Animal update failed due to a conflict")

    async def soft_delete(self, animal_id: UUID) -> None:
        animal = await self.get_by_id(animal_id)
        if animal.status not in ("deceased", "transferred"):
            raise ValidationException(
                "Can only soft-delete animals with status 'deceased' or 'transferred'"
            )
        await self.repo.soft_delete(animal)

    async def list_transfers(
        self, animal_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[AnimalTransfer]:
        await self.get_by_id(animal_id)
        return await self.transfer_repo.list_by_animal(
            animal_id, skip=skip, limit=limit
        )

    async def create_transfer(
        self, data: AnimalTransferCreate, employee_repo: EmployeeRepository
    ) -> AnimalTransfer:
        # Validate animal exists and is active
        animal = await self.get_by_id(data.animal_id)
        if animal.status != "active":
            raise ValidationException("Can only transfer active animals")

        # Validate employee exists and is active
        employee = await employee_repo.get_by_id(data.employee_id)
        if not employee:
            raise NotFoundException("Employee not found")
        if employee.status != "active":
            raise ValidationException("Only active employees can authorize transfers")

        # Validate origin enclosure exists
        origin = await self.enclosure_repo.get_by_id(data.origin_enclosure_id)
        if not origin:
            raise NotFoundException("Origin enclosure not found")

        # Validate destination enclosure exists and is active
        dest = await self.enclosure_repo.get_by_id(data.destination_enclosure_id)
        if not dest:
            raise NotFoundException("Destination enclosure not found")
        if dest.status not in ("active",):
            raise ValidationException("Cannot transfer to an inactive enclosure")

        # Validate different enclosures
        if data.origin_enclosure_id == data.destination_enclosure_id:
            raise ValidationException(
                "Origin and destination enclosures must be different"
            )

        if animal.enclosure_id != data.origin_enclosure_id:
            raise ValidationException(
                "Animal is not currently in the provided origin enclosure"
            )

        # Validate capacity
        current_count = await self.repo.count_by_enclosure(
            data.destination_enclosure_id
        )
        if current_count >= dest.capacity:
            raise ValidationException(
                "Destination enclosure has reached maximum capacity"
            )

        # Create transfer and update animal enclosure in same transaction
        transfer = AnimalTransfer(
            animal_id=data.animal_id,
            origin_enclosure_id=data.origin_enclosure_id,
            destination_enclosure_id=data.destination_enclosure_id,
            employee_id=data.employee_id,
            transfer_date=data.transfer_date,
            reason=data.reason,
        )
        transfer = await self.transfer_repo.create(transfer)
        await self.repo.update_enclosure(animal, data.destination_enclosure_id)
        return transfer

    async def get_transfer_by_id(self, transfer_id: UUID) -> AnimalTransfer:
        transfer = await self.transfer_repo.get_by_id(transfer_id)
        if not transfer:
            raise NotFoundException("Transfer not found")
        return transfer
