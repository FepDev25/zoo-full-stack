from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, paginate
from app.modules.animals.repository import AnimalRepository
from app.modules.health.repository import (
    MedicalRecordRepository,
    MedicalVaccinationRepository,
    VaccineRepository,
)
from app.modules.health.schemas import (
    MedicalRecordCreate,
    MedicalRecordRead,
    MedicalRecordUpdate,
    MedicalVaccinationCreate,
    MedicalVaccinationRead,
    MedicalVaccinationUpdate,
    VaccineCreate,
    VaccineRead,
    VaccineUpdate,
)
from app.modules.health.service import (
    MedicalRecordService,
    MedicalVaccinationService,
    VaccineService,
)
from app.modules.personnel.repository import EmployeeRepository

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/medical-records", response_model=list[MedicalRecordRead])
async def list_medical_records(
    pagination: dict = Depends(paginate),
    db: AsyncSession = Depends(get_db),
):
    service = MedicalRecordService(
        MedicalRecordRepository(db),
        AnimalRepository(db),
        EmployeeRepository(db),
    )
    return await service.list_all(**pagination)


@router.post(
    "/medical-records",
    response_model=MedicalRecordRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_medical_record(
    data: MedicalRecordCreate,
    db: AsyncSession = Depends(get_db),
):
    service = MedicalRecordService(
        MedicalRecordRepository(db),
        AnimalRepository(db),
        EmployeeRepository(db),
    )
    return await service.create(data)


@router.get("/medical-records/{record_id}", response_model=MedicalRecordRead)
async def get_medical_record(record_id: UUID, db: AsyncSession = Depends(get_db)):
    service = MedicalRecordService(
        MedicalRecordRepository(db),
        AnimalRepository(db),
        EmployeeRepository(db),
    )
    return await service.get_by_id(record_id)


@router.put("/medical-records/{record_id}", response_model=MedicalRecordRead)
async def update_medical_record(
    record_id: UUID,
    data: MedicalRecordUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = MedicalRecordService(
        MedicalRecordRepository(db),
        AnimalRepository(db),
        EmployeeRepository(db),
    )
    return await service.update(record_id, data)


@router.get("/vaccines", response_model=list[VaccineRead])
async def list_vaccines(
    pagination: dict = Depends(paginate),
    db: AsyncSession = Depends(get_db),
):
    service = VaccineService(VaccineRepository(db))
    return await service.list_all(**pagination)


@router.post(
    "/vaccines", response_model=VaccineRead, status_code=status.HTTP_201_CREATED
)
async def create_vaccine(data: VaccineCreate, db: AsyncSession = Depends(get_db)):
    service = VaccineService(VaccineRepository(db))
    return await service.create(data)


@router.get("/vaccines/{vaccine_id}", response_model=VaccineRead)
async def get_vaccine(vaccine_id: UUID, db: AsyncSession = Depends(get_db)):
    service = VaccineService(VaccineRepository(db))
    return await service.get_by_id(vaccine_id)


@router.put("/vaccines/{vaccine_id}", response_model=VaccineRead)
async def update_vaccine(
    vaccine_id: UUID,
    data: VaccineUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = VaccineService(VaccineRepository(db))
    return await service.update(vaccine_id, data)


@router.delete("/vaccines/{vaccine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vaccine(vaccine_id: UUID, db: AsyncSession = Depends(get_db)):
    service = VaccineService(VaccineRepository(db))
    await service.delete(vaccine_id)


@router.get("/vaccinations", response_model=list[MedicalVaccinationRead])
async def list_vaccinations(
    pagination: dict = Depends(paginate),
    db: AsyncSession = Depends(get_db),
):
    service = MedicalVaccinationService(
        MedicalVaccinationRepository(db),
        MedicalRecordRepository(db),
        VaccineRepository(db),
    )
    return await service.list_all(**pagination)


@router.post(
    "/vaccinations",
    response_model=MedicalVaccinationRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_vaccination(
    data: MedicalVaccinationCreate,
    db: AsyncSession = Depends(get_db),
):
    service = MedicalVaccinationService(
        MedicalVaccinationRepository(db),
        MedicalRecordRepository(db),
        VaccineRepository(db),
    )
    return await service.create(data)


@router.get("/vaccinations/{vaccination_id}", response_model=MedicalVaccinationRead)
async def get_vaccination(vaccination_id: UUID, db: AsyncSession = Depends(get_db)):
    service = MedicalVaccinationService(
        MedicalVaccinationRepository(db),
        MedicalRecordRepository(db),
        VaccineRepository(db),
    )
    return await service.get_by_id(vaccination_id)


@router.put("/vaccinations/{vaccination_id}", response_model=MedicalVaccinationRead)
async def update_vaccination(
    vaccination_id: UUID,
    data: MedicalVaccinationUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = MedicalVaccinationService(
        MedicalVaccinationRepository(db),
        MedicalRecordRepository(db),
        VaccineRepository(db),
    )
    return await service.update(vaccination_id, data)
