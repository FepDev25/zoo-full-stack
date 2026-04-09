import logging
from datetime import timedelta
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.exceptions import ConflictException, NotFoundException, ValidationException
from app.modules.animals.repository import AnimalRepository
from app.modules.health.models import MedicalRecord, Vaccine, MedicalVaccination
from app.modules.health.repository import (
    MedicalRecordRepository,
    MedicalVaccinationRepository,
    VaccineRepository,
)
from app.modules.health.schemas import (
    MedicalRecordCreate,
    MedicalRecordUpdate,
    MedicalVaccinationCreate,
    MedicalVaccinationUpdate,
    VaccineCreate,
    VaccineUpdate,
)
from app.modules.personnel.repository import EmployeeRepository

logger = logging.getLogger(__name__)

# servicios para logica de negocio de salud
class MedicalRecordService:
    def __init__(
        self,
        repo: MedicalRecordRepository,
        animal_repo: AnimalRepository,
        employee_repo: EmployeeRepository,
    ):
        self.repo = repo
        self.animal_repo = animal_repo
        self.employee_repo = employee_repo

    async def list_all(self, skip: int = 0, limit: int = 20) -> list[MedicalRecord]:
        return await self.repo.list(skip=skip, limit=limit)

    async def get_by_id(self, record_id: UUID) -> MedicalRecord:
        record = await self.repo.get_by_id(record_id)
        if not record:
            raise NotFoundException("Medical record not found")
        return record

    async def create(self, data: MedicalRecordCreate) -> MedicalRecord:
        animal = await self.animal_repo.get_by_id(data.animal_id)
        if not animal:
            raise NotFoundException("Animal not found")
        if animal.status == "deceased":
            raise ValidationException(
                "Cannot create medical records for deceased animals"
            )

        employee = await self.employee_repo.get_by_id(data.performed_by)
        if not employee:
            raise NotFoundException("Employee not found")
        if employee.status != "active":
            raise ValidationException("Medical records require an active employee")

        role_names = {role.name.lower() for role in employee.roles}
        if not any("veter" in role for role in role_names):
            logger.warning(
                "Employee %s created medical record without veterinarian role",
                employee.id,
            )

        record = MedicalRecord(
            animal_id=data.animal_id,
            performed_by=data.performed_by,
            visit_date=data.visit_date,
            diagnosis=data.diagnosis,
            treatment=data.treatment,
            observations=data.observations,
            urgency_level=data.urgency_level.value,
        )
        return await self.repo.create(record)

    async def update(self, record_id: UUID, data: MedicalRecordUpdate) -> MedicalRecord:
        record = await self.get_by_id(record_id)
        if data.visit_date is not None:
            record.visit_date = data.visit_date
        if data.diagnosis is not None:
            record.diagnosis = data.diagnosis
        if data.treatment is not None:
            record.treatment = data.treatment
        if data.observations is not None:
            record.observations = data.observations
        if data.urgency_level is not None:
            record.urgency_level = data.urgency_level.value
        return await self.repo.update(record)


class VaccineService:
    def __init__(self, repo: VaccineRepository):
        self.repo = repo

    async def list_all(self, skip: int = 0, limit: int = 20) -> list[Vaccine]:
        return await self.repo.list(skip=skip, limit=limit)

    async def get_by_id(self, vaccine_id: UUID) -> Vaccine:
        vaccine = await self.repo.get_by_id(vaccine_id)
        if not vaccine:
            raise NotFoundException("Vaccine not found")
        return vaccine

    async def create(self, data: VaccineCreate) -> Vaccine:
        existing = await self.repo.get_by_name(data.name)
        if existing:
            raise ConflictException(f"Vaccine with name '{data.name}' already exists")
        vaccine = Vaccine(
            name=data.name,
            description=data.description,
            validity_period=data.validity_period,
        )
        try:
            return await self.repo.create(vaccine)
        except IntegrityError:
            raise ConflictException("Vaccine creation failed due to a conflict")

    async def update(self, vaccine_id: UUID, data: VaccineUpdate) -> Vaccine:
        vaccine = await self.get_by_id(vaccine_id)
        if data.name is not None:
            existing = await self.repo.get_by_name(data.name)
            if existing and existing.id != vaccine_id:
                raise ConflictException(
                    f"Vaccine with name '{data.name}' already exists"
                )
            vaccine.name = data.name
        if data.description is not None:
            vaccine.description = data.description
        if data.validity_period is not None:
            vaccine.validity_period = data.validity_period
        try:
            return await self.repo.update(vaccine)
        except IntegrityError:
            raise ConflictException("Vaccine update failed due to a conflict")

    async def delete(self, vaccine_id: UUID) -> None:
        await self.get_by_id(vaccine_id)
        await self.repo.delete(vaccine_id)


class MedicalVaccinationService:
    def __init__(
        self,
        repo: MedicalVaccinationRepository,
        medical_record_repo: MedicalRecordRepository,
        vaccine_repo: VaccineRepository,
    ):
        self.repo = repo
        self.medical_record_repo = medical_record_repo
        self.vaccine_repo = vaccine_repo

    async def list_all(
        self, skip: int = 0, limit: int = 20
    ) -> list[MedicalVaccination]:
        return await self.repo.list(skip=skip, limit=limit)

    async def get_by_id(self, vaccination_id: UUID) -> MedicalVaccination:
        vaccination = await self.repo.get_by_id(vaccination_id)
        if not vaccination:
            raise NotFoundException("Medical vaccination not found")
        return vaccination

    async def create(self, data: MedicalVaccinationCreate) -> MedicalVaccination:
        record = await self.medical_record_repo.get_by_id(data.medical_record_id)
        if not record:
            raise NotFoundException("Medical record not found")

        vaccine = await self.vaccine_repo.get_by_id(data.vaccine_id)
        if not vaccine:
            raise NotFoundException("Vaccine not found")

        next_due_date = data.next_due_date
        if next_due_date is None and vaccine.validity_period is not None:
            next_due_date = data.application_date + vaccine.validity_period

        vaccination = MedicalVaccination(
            medical_record_id=data.medical_record_id,
            vaccine_id=data.vaccine_id,
            application_date=data.application_date,
            next_due_date=next_due_date,
            batch_number=data.batch_number,
            notes=data.notes,
        )
        return await self.repo.create(vaccination)

    async def update(
        self, vaccination_id: UUID, data: MedicalVaccinationUpdate
    ) -> MedicalVaccination:
        vaccination = await self.get_by_id(vaccination_id)
        if data.application_date is not None:
            vaccination.application_date = data.application_date
        if data.next_due_date is not None:
            vaccination.next_due_date = data.next_due_date
        if data.batch_number is not None:
            vaccination.batch_number = data.batch_number
        if data.notes is not None:
            vaccination.notes = data.notes
        return await self.repo.update(vaccination)
