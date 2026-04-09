from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.exceptions import (
    ConflictException,
    NotFoundException,
    ValidationException,
)
from app.modules.personnel.models import Department, Employee, EmployeeRole, Role
from app.modules.personnel.repository import (
    DepartmentRepository,
    EmployeeRepository,
    RoleRepository,
)
from app.modules.personnel.schemas import (
    DepartmentCreate,
    DepartmentUpdate,
    EmployeeCreate,
    EmployeeRoleCreate,
    EmployeeUpdate,
    RoleCreate,
    RoleUpdate,
)

# servicios de negocio para departamentos, roles y empleados

class DepartmentService:
    def __init__(self, repo: DepartmentRepository, employee_repo: EmployeeRepository):
        self.repo = repo
        self.employee_repo = employee_repo

    async def list_all(self, skip: int = 0, limit: int = 20) -> list[Department]:
        return await self.repo.list(skip=skip, limit=limit)

    async def get_by_id(self, department_id: UUID) -> Department:
        department = await self.repo.get_by_id(department_id)
        if not department:
            raise NotFoundException("Department not found")
        return department

    async def create(self, data: DepartmentCreate) -> Department:
        existing = await self.repo.get_by_name(data.name)
        if existing:
            raise ConflictException(
                f"Department with name '{data.name}' already exists"
            )
        department = Department(
            name=data.name,
            description=data.description,
            status=data.status.value,
        )
        return await self.repo.create(department)

    async def update(self, department_id: UUID, data: DepartmentUpdate) -> Department:
        department = await self.get_by_id(department_id)
        if data.name is not None:
            existing = await self.repo.get_by_name(data.name)
            if existing and existing.id != department_id:
                raise ConflictException(
                    f"Department with name '{data.name}' already exists"
                )
            department.name = data.name
        if data.description is not None:
            department.description = data.description
        if data.status is not None:
            department.status = data.status.value
        return await self.repo.update(department)

    async def delete(self, department_id: UUID) -> None:
        department = await self.get_by_id(department_id)
        active_count = await self.employee_repo.count_active(department_id)
        if active_count > 0:
            raise ValidationException(
                f"Cannot delete department: {active_count} active employee(s) are assigned"
            )
        await self.repo.delete(department_id)


class RoleService:
    def __init__(self, repo: RoleRepository):
        self.repo = repo

    async def list_all(self, skip: int = 0, limit: int = 20) -> list[Role]:
        return await self.repo.list(skip=skip, limit=limit)

    async def get_by_id(self, role_id: UUID) -> Role:
        role = await self.repo.get_by_id(role_id)
        if not role:
            raise NotFoundException("Role not found")
        return role

    async def create(self, data: RoleCreate) -> Role:
        existing = await self.repo.get_by_name(data.name)
        if existing:
            raise ConflictException(f"Role with name '{data.name}' already exists")
        role = Role(name=data.name, description=data.description)
        return await self.repo.create(role)

    async def update(self, role_id: UUID, data: RoleUpdate) -> Role:
        role = await self.get_by_id(role_id)
        if data.name is not None:
            existing = await self.repo.get_by_name(data.name)
            if existing and existing.id != role_id:
                raise ConflictException(f"Role with name '{data.name}' already exists")
            role.name = data.name
        if data.description is not None:
            role.description = data.description
        return await self.repo.update(role)

    async def delete(self, role_id: UUID) -> None:
        await self.get_by_id(role_id)
        await self.repo.delete(role_id)


class EmployeeService:
    def __init__(self, repo: EmployeeRepository, role_repo: RoleRepository):
        self.repo = repo
        self.role_repo = role_repo

    async def list_all(self, skip: int = 0, limit: int = 20) -> list[Employee]:
        return await self.repo.list_active(skip=skip, limit=limit)

    async def get_by_id(self, employee_id: UUID) -> Employee:
        employee = await self.repo.get_by_id(employee_id)
        if not employee:
            raise NotFoundException("Employee not found")
        return employee

    async def create(self, data: EmployeeCreate) -> Employee:
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise ConflictException(
                f"Employee with email '{data.email}' already exists"
            )
        try:
            employee = Employee(
                full_name=data.full_name,
                email=data.email,
                phone=data.phone,
                hire_date=data.hire_date,
                birth_date=data.birth_date,
                department_id=data.department_id,
                status=data.status.value,
            )
            return await self.repo.create(employee)
        except IntegrityError:
            raise ConflictException("Employee creation failed due to a conflict")

    async def update(self, employee_id: UUID, data: EmployeeUpdate) -> Employee:
        employee = await self.get_by_id(employee_id)
        if data.email is not None:
            existing = await self.repo.get_by_email(data.email)
            if existing and existing.id != employee_id:
                raise ConflictException(
                    f"Employee with email '{data.email}' already exists"
                )
            employee.email = data.email
        if data.full_name is not None:
            employee.full_name = data.full_name
        if data.phone is not None:
            employee.phone = data.phone
        if data.hire_date is not None:
            employee.hire_date = data.hire_date
        if data.birth_date is not None:
            employee.birth_date = data.birth_date
        if data.department_id is not None:
            employee.department_id = data.department_id
        if data.status is not None:
            employee.status = data.status.value
        try:
            return await self.repo.update(employee)
        except IntegrityError:
            raise ConflictException("Employee update failed due to a conflict")

    async def soft_delete(self, employee_id: UUID) -> None:
        employee = await self.get_by_id(employee_id)
        await self.repo.soft_delete(employee)

    async def add_role(
        self, employee_id: UUID, data: EmployeeRoleCreate
    ) -> EmployeeRole:
        await self.get_by_id(employee_id)
        role = await self.role_repo.get_by_id(data.role_id)
        if not role:
            raise NotFoundException("Role not found")
        already = await self.repo.has_role(employee_id, data.role_id)
        if already:
            raise ConflictException("Employee already has this role")
        employee_role = EmployeeRole(
            employee_id=employee_id,
            role_id=data.role_id,
        )
        return await self.repo.add_role(employee_role)

    async def remove_role(self, employee_id: UUID, role_id: UUID) -> None:
        await self.get_by_id(employee_id)
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise NotFoundException("Role not found")
        if not await self.repo.has_role(employee_id, role_id):
            raise NotFoundException("Employee does not have this role")
        await self.repo.remove_role(employee_id, role_id)
