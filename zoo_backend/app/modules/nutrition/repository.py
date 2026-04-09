from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.nutrition.models import Diet, FeedingSchedule


class DietRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self, skip: int = 0, limit: int = 20) -> list[Diet]:
        stmt = (
            select(Diet)
            .options(selectinload(Diet.feeding_schedules))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, diet_id: UUID) -> Diet | None:
        stmt = (
            select(Diet)
            .options(selectinload(Diet.feeding_schedules))
            .where(Diet.id == diet_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_by_animal(self, animal_id: UUID) -> Diet | None:
        stmt = select(Diet).where(
            and_(
                Diet.animal_id == animal_id,
                Diet.effective_to.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, diet: Diet) -> Diet:
        self.db.add(diet)
        await self.db.flush()
        await self.db.refresh(diet)
        return diet

    async def update(self, diet: Diet) -> Diet:
        await self.db.flush()
        await self.db.refresh(diet)
        return diet

    async def close_active_for_animal(
        self, animal_id: UUID, close_at: datetime
    ) -> None:
        active = await self.get_active_by_animal(animal_id)
        if active is not None:
            active.effective_to = close_at
            await self.db.flush()

    async def delete(self, diet_id: UUID) -> None:
        stmt = delete(Diet).where(Diet.id == diet_id)
        await self.db.execute(stmt)
        await self.db.flush()


class FeedingScheduleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self, skip: int = 0, limit: int = 20) -> list[FeedingSchedule]:
        stmt = select(FeedingSchedule).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, schedule_id: UUID) -> FeedingSchedule | None:
        stmt = select(FeedingSchedule).where(FeedingSchedule.id == schedule_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, schedule: FeedingSchedule) -> FeedingSchedule:
        self.db.add(schedule)
        await self.db.flush()
        await self.db.refresh(schedule)
        return schedule

    async def update(self, schedule: FeedingSchedule) -> FeedingSchedule:
        await self.db.flush()
        await self.db.refresh(schedule)
        return schedule

    async def delete(self, schedule_id: UUID) -> None:
        stmt = delete(FeedingSchedule).where(FeedingSchedule.id == schedule_id)
        await self.db.execute(stmt)
        await self.db.flush()
