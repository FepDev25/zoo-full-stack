from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.animals.models import (
    Animal,
    AnimalTransfer,
    Enclosure,
    Species,
    Zone,
)

# repositorio de especies
class SpeciesRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self, skip: int = 0, limit: int = 20) -> list[Species]:
        stmt = select(Species).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, species_id: UUID) -> Species | None:
        stmt = select(Species).where(Species.id == species_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_common_name(self, common_name: str) -> Species | None:
        stmt = select(Species).where(Species.common_name == common_name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_scientific_name(self, scientific_name: str) -> Species | None:
        stmt = select(Species).where(Species.scientific_name == scientific_name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, species: Species) -> Species:
        self.db.add(species)
        await self.db.flush()
        await self.db.refresh(species)
        return species

    async def update(self, species: Species) -> Species:
        await self.db.flush()
        await self.db.refresh(species)
        return species

    async def delete(self, species_id: UUID) -> None:
        stmt = delete(Species).where(Species.id == species_id)
        await self.db.execute(stmt)
        await self.db.flush()

# repositorio de zonas
class ZoneRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self, skip: int = 0, limit: int = 20) -> list[Zone]:
        stmt = select(Zone).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, zone_id: UUID) -> Zone | None:
        stmt = select(Zone).where(Zone.id == zone_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Zone | None:
        stmt = select(Zone).where(Zone.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, zone: Zone) -> Zone:
        self.db.add(zone)
        await self.db.flush()
        await self.db.refresh(zone)
        return zone

    async def update(self, zone: Zone) -> Zone:
        await self.db.flush()
        await self.db.refresh(zone)
        return zone

    async def delete(self, zone_id: UUID) -> None:
        stmt = delete(Zone).where(Zone.id == zone_id)
        await self.db.execute(stmt)
        await self.db.flush()

    async def has_enclosures(self, zone_id: UUID) -> bool:
        stmt = select(Enclosure.id).where(Enclosure.zone_id == zone_id).limit(1)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

# repositorio de recintos
class EnclosureRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self, skip: int = 0, limit: int = 20) -> list[Enclosure]:
        stmt = (
            select(Enclosure)
            .options(selectinload(Enclosure.zone))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, enclosure_id: UUID) -> Enclosure | None:
        stmt = (
            select(Enclosure)
            .options(selectinload(Enclosure.zone))
            .where(Enclosure.id == enclosure_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Enclosure | None:
        stmt = select(Enclosure).where(Enclosure.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def count_animals(self, enclosure_id: UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(Animal)
            .where(
                and_(
                    Animal.enclosure_id == enclosure_id,
                    Animal.deleted_at.is_(None),
                )
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def create(self, enclosure: Enclosure) -> Enclosure:
        self.db.add(enclosure)
        await self.db.flush()
        await self.db.refresh(enclosure)
        return enclosure

    async def update(self, enclosure: Enclosure) -> Enclosure:
        await self.db.flush()
        await self.db.refresh(enclosure)
        return enclosure

    async def delete(self, enclosure_id: UUID) -> None:
        stmt = delete(Enclosure).where(Enclosure.id == enclosure_id)
        await self.db.execute(stmt)
        await self.db.flush()

# repositorio de animales
class AnimalRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_active(self, skip: int = 0, limit: int = 20) -> list[Animal]:
        stmt = (
            select(Animal)
            .options(
                selectinload(Animal.species),
                selectinload(Animal.enclosure),
            )
            .where(Animal.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, animal_id: UUID) -> Animal | None:
        stmt = (
            select(Animal)
            .options(
                selectinload(Animal.species),
                selectinload(Animal.enclosure),
            )
            .where(and_(Animal.id == animal_id, Animal.deleted_at.is_(None)))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_enclosure(
        self, enclosure_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[Animal]:
        stmt = (
            select(Animal)
            .options(
                selectinload(Animal.species),
                selectinload(Animal.enclosure),
            )
            .where(
                and_(
                    Animal.enclosure_id == enclosure_id,
                    Animal.deleted_at.is_(None),
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_enclosure(self, enclosure_id: UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(Animal)
            .where(
                and_(
                    Animal.enclosure_id == enclosure_id,
                    Animal.deleted_at.is_(None),
                )
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def create(self, animal: Animal) -> Animal:
        self.db.add(animal)
        await self.db.flush()
        await self.db.refresh(animal)
        return animal

    async def update(self, animal: Animal) -> Animal:
        await self.db.flush()
        await self.db.refresh(animal)
        return animal

    async def soft_delete(self, animal: Animal) -> None:
        animal.deleted_at = datetime.now(timezone.utc)
        await self.db.flush()

    async def update_enclosure(self, animal: Animal, new_enclosure_id: UUID) -> None:
        animal.enclosure_id = new_enclosure_id
        await self.db.flush()

# repositorio de transferencias de animales
class AnimalTransferRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_animal(
        self, animal_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[AnimalTransfer]:
        stmt = (
            select(AnimalTransfer)
            .where(AnimalTransfer.animal_id == animal_id)
            .order_by(AnimalTransfer.transfer_date.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, transfer_id: UUID) -> AnimalTransfer | None:
        stmt = (
            select(AnimalTransfer)
            .options(
                selectinload(AnimalTransfer.animal),
                selectinload(AnimalTransfer.origin_enclosure),
                selectinload(AnimalTransfer.destination_enclosure),
            )
            .where(AnimalTransfer.id == transfer_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, transfer: AnimalTransfer) -> AnimalTransfer:
        self.db.add(transfer)
        await self.db.flush()
        await self.db.refresh(transfer)
        return transfer
