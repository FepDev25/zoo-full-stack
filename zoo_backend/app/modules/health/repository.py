from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.health.models import MedicalRecord, Vaccine, MedicalVaccination

# repositorios para acceso a datos de salud
class MedicalRecordRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self, skip: int = 0, limit: int = 20) -> list[MedicalRecord]:
        stmt = (
            select(MedicalRecord)
            .options(
                selectinload(MedicalRecord.animal),
                selectinload(MedicalRecord.performer),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, record_id: UUID) -> MedicalRecord | None:
        stmt = (
            select(MedicalRecord)
            .options(
                selectinload(MedicalRecord.animal),
                selectinload(MedicalRecord.performer),
                selectinload(MedicalRecord.vaccinations),
            )
            .where(MedicalRecord.id == record_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, record: MedicalRecord) -> MedicalRecord:
        self.db.add(record)
        await self.db.flush()
        await self.db.refresh(record)
        return record

    async def update(self, record: MedicalRecord) -> MedicalRecord:
        await self.db.flush()
        await self.db.refresh(record)
        return record


class VaccineRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self, skip: int = 0, limit: int = 20) -> list[Vaccine]:
        stmt = select(Vaccine).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, vaccine_id: UUID) -> Vaccine | None:
        stmt = select(Vaccine).where(Vaccine.id == vaccine_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Vaccine | None:
        stmt = select(Vaccine).where(Vaccine.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, vaccine: Vaccine) -> Vaccine:
        self.db.add(vaccine)
        await self.db.flush()
        await self.db.refresh(vaccine)
        return vaccine

    async def update(self, vaccine: Vaccine) -> Vaccine:
        await self.db.flush()
        await self.db.refresh(vaccine)
        return vaccine

    async def delete(self, vaccine_id: UUID) -> None:
        stmt = delete(Vaccine).where(Vaccine.id == vaccine_id)
        await self.db.execute(stmt)
        await self.db.flush()


class MedicalVaccinationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self, skip: int = 0, limit: int = 20) -> list[MedicalVaccination]:
        stmt = (
            select(MedicalVaccination)
            .options(
                selectinload(MedicalVaccination.medical_record),
                selectinload(MedicalVaccination.vaccine),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, vaccination_id: UUID) -> MedicalVaccination | None:
        stmt = (
            select(MedicalVaccination)
            .options(
                selectinload(MedicalVaccination.medical_record),
                selectinload(MedicalVaccination.vaccine),
            )
            .where(MedicalVaccination.id == vaccination_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, vaccination: MedicalVaccination) -> MedicalVaccination:
        self.db.add(vaccination)
        await self.db.flush()
        await self.db.refresh(vaccination)
        return vaccination

    async def update(self, vaccination: MedicalVaccination) -> MedicalVaccination:
        await self.db.flush()
        await self.db.refresh(vaccination)
        return vaccination
