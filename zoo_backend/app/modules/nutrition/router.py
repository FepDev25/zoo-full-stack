from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, paginate
from app.modules.animals.repository import AnimalRepository
from app.modules.nutrition.repository import DietRepository, FeedingScheduleRepository
from app.modules.nutrition.schemas import (
    DietCreate,
    DietRead,
    DietUpdate,
    FeedingScheduleCreate,
    FeedingScheduleRead,
    FeedingScheduleUpdate,
)
from app.modules.nutrition.service import DietService, FeedingScheduleService
from app.modules.personnel.repository import EmployeeRepository

router = APIRouter(prefix="/nutrition", tags=["Nutrition"])


@router.get("/diets", response_model=list[DietRead])
async def list_diets(
    pagination: dict = Depends(paginate),
    db: AsyncSession = Depends(get_db),
):
    service = DietService(
        DietRepository(db), AnimalRepository(db), EmployeeRepository(db)
    )
    return await service.list_all(**pagination)


@router.post("/diets", response_model=DietRead, status_code=status.HTTP_201_CREATED)
async def create_diet(data: DietCreate, db: AsyncSession = Depends(get_db)):
    service = DietService(
        DietRepository(db), AnimalRepository(db), EmployeeRepository(db)
    )
    return await service.create(data)


@router.get("/diets/{diet_id}", response_model=DietRead)
async def get_diet(diet_id: UUID, db: AsyncSession = Depends(get_db)):
    service = DietService(
        DietRepository(db), AnimalRepository(db), EmployeeRepository(db)
    )
    return await service.get_by_id(diet_id)


@router.put("/diets/{diet_id}", response_model=DietRead)
async def update_diet(
    diet_id: UUID, data: DietUpdate, db: AsyncSession = Depends(get_db)
):
    service = DietService(
        DietRepository(db), AnimalRepository(db), EmployeeRepository(db)
    )
    return await service.update(diet_id, data)


@router.delete("/diets/{diet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diet(diet_id: UUID, db: AsyncSession = Depends(get_db)):
    service = DietService(
        DietRepository(db), AnimalRepository(db), EmployeeRepository(db)
    )
    await service.delete(diet_id)


@router.get("/feeding-schedules", response_model=list[FeedingScheduleRead])
async def list_feeding_schedules(
    pagination: dict = Depends(paginate),
    db: AsyncSession = Depends(get_db),
):
    service = FeedingScheduleService(
        FeedingScheduleRepository(db),
        DietRepository(db),
        EmployeeRepository(db),
    )
    return await service.list_all(**pagination)


@router.post(
    "/feeding-schedules",
    response_model=FeedingScheduleRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_feeding_schedule(
    data: FeedingScheduleCreate,
    db: AsyncSession = Depends(get_db),
):
    service = FeedingScheduleService(
        FeedingScheduleRepository(db),
        DietRepository(db),
        EmployeeRepository(db),
    )
    return await service.create(data)


@router.get("/feeding-schedules/{schedule_id}", response_model=FeedingScheduleRead)
async def get_feeding_schedule(schedule_id: UUID, db: AsyncSession = Depends(get_db)):
    service = FeedingScheduleService(
        FeedingScheduleRepository(db),
        DietRepository(db),
        EmployeeRepository(db),
    )
    return await service.get_by_id(schedule_id)


@router.put("/feeding-schedules/{schedule_id}", response_model=FeedingScheduleRead)
async def update_feeding_schedule(
    schedule_id: UUID,
    data: FeedingScheduleUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = FeedingScheduleService(
        FeedingScheduleRepository(db),
        DietRepository(db),
        EmployeeRepository(db),
    )
    return await service.update(schedule_id, data)


@router.delete(
    "/feeding-schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_feeding_schedule(
    schedule_id: UUID, db: AsyncSession = Depends(get_db)
):
    service = FeedingScheduleService(
        FeedingScheduleRepository(db),
        DietRepository(db),
        EmployeeRepository(db),
    )
    await service.delete(schedule_id)
