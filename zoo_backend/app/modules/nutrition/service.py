from datetime import datetime, timezone
from uuid import UUID

from app.exceptions import NotFoundException, ValidationException
from app.modules.animals.repository import AnimalRepository
from app.modules.nutrition.models import Diet, FeedingSchedule
from app.modules.nutrition.repository import DietRepository, FeedingScheduleRepository
from app.modules.nutrition.schemas import (
    DietCreate,
    DietUpdate,
    FeedingScheduleCreate,
    FeedingScheduleUpdate,
)
from app.modules.personnel.repository import EmployeeRepository


class DietService:
    def __init__(
        self,
        repo: DietRepository,
        animal_repo: AnimalRepository,
        employee_repo: EmployeeRepository,
    ):
        self.repo = repo
        self.animal_repo = animal_repo
        self.employee_repo = employee_repo

    async def list_all(self, skip: int = 0, limit: int = 20) -> list[Diet]:
        return await self.repo.list(skip=skip, limit=limit)

    async def get_by_id(self, diet_id: UUID) -> Diet:
        diet = await self.repo.get_by_id(diet_id)
        if not diet:
            raise NotFoundException("Diet not found")
        return diet

    async def create(self, data: DietCreate) -> Diet:
        animal = await self.animal_repo.get_by_id(data.animal_id)
        if not animal:
            raise NotFoundException("Animal not found")
        if animal.status == "deceased":
            raise ValidationException("Cannot assign diets to deceased animals")

        designer = await self.employee_repo.get_by_id(data.designed_by)
        if not designer:
            raise NotFoundException("Designer employee not found")
        if designer.status != "active":
            raise ValidationException("Diet designer must be an active employee")

        now = datetime.now(timezone.utc)
        effective_from = data.effective_from or now

        await self.repo.close_active_for_animal(data.animal_id, effective_from)

        diet = Diet(
            animal_id=data.animal_id,
            designed_by=data.designed_by,
            name=data.name,
            description=data.description,
            daily_rations=[item.model_dump() for item in data.daily_rations],
            effective_from=effective_from,
            effective_to=data.effective_to,
        )
        return await self.repo.create(diet)

    async def update(self, diet_id: UUID, data: DietUpdate) -> Diet:
        diet = await self.get_by_id(diet_id)

        if data.designed_by is not None:
            designer = await self.employee_repo.get_by_id(data.designed_by)
            if not designer:
                raise NotFoundException("Designer employee not found")
            if designer.status != "active":
                raise ValidationException("Diet designer must be an active employee")
            diet.designed_by = data.designed_by

        if data.name is not None:
            diet.name = data.name
        if data.description is not None:
            diet.description = data.description
        if data.daily_rations is not None:
            diet.daily_rations = [item.model_dump() for item in data.daily_rations]
        if data.effective_from is not None:
            diet.effective_from = data.effective_from
        if data.effective_to is not None:
            diet.effective_to = data.effective_to

        if diet.effective_to is not None and diet.effective_from >= diet.effective_to:
            raise ValidationException("effective_from must be before effective_to")

        return await self.repo.update(diet)

    async def delete(self, diet_id: UUID) -> None:
        await self.get_by_id(diet_id)
        await self.repo.delete(diet_id)


class FeedingScheduleService:
    def __init__(
        self,
        repo: FeedingScheduleRepository,
        diet_repo: DietRepository,
        employee_repo: EmployeeRepository,
    ):
        self.repo = repo
        self.diet_repo = diet_repo
        self.employee_repo = employee_repo

    async def list_all(self, skip: int = 0, limit: int = 20) -> list[FeedingSchedule]:
        return await self.repo.list(skip=skip, limit=limit)

    async def get_by_id(self, schedule_id: UUID) -> FeedingSchedule:
        schedule = await self.repo.get_by_id(schedule_id)
        if not schedule:
            raise NotFoundException("Feeding schedule not found")
        return schedule

    async def create(self, data: FeedingScheduleCreate) -> FeedingSchedule:
        diet = await self.diet_repo.get_by_id(data.diet_id)
        if not diet:
            raise NotFoundException("Diet not found")

        assignee = await self.employee_repo.get_by_id(data.assigned_to)
        if not assignee:
            raise NotFoundException("Assigned employee not found")
        if assignee.status != "active":
            raise ValidationException("Feeding assignee must be an active employee")

        schedule = FeedingSchedule(
            diet_id=data.diet_id,
            assigned_to=data.assigned_to,
            feeding_time=data.feeding_time,
            frequency=data.frequency.value,
            instructions=data.instructions,
            status=data.status.value,
        )
        return await self.repo.create(schedule)

    async def update(
        self, schedule_id: UUID, data: FeedingScheduleUpdate
    ) -> FeedingSchedule:
        schedule = await self.get_by_id(schedule_id)

        if data.assigned_to is not None:
            assignee = await self.employee_repo.get_by_id(data.assigned_to)
            if not assignee:
                raise NotFoundException("Assigned employee not found")
            if assignee.status != "active":
                raise ValidationException("Feeding assignee must be an active employee")
            schedule.assigned_to = data.assigned_to

        if data.feeding_time is not None:
            schedule.feeding_time = data.feeding_time
        if data.frequency is not None:
            schedule.frequency = data.frequency.value
        if data.instructions is not None:
            schedule.instructions = data.instructions
        if data.status is not None:
            schedule.status = data.status.value

        return await self.repo.update(schedule)

    async def delete(self, schedule_id: UUID) -> None:
        await self.get_by_id(schedule_id)
        await self.repo.delete(schedule_id)
