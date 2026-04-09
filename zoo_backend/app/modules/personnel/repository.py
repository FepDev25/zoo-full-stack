from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.personnel.models import Department, Employee, EmployeeRole, Role

# repositorios de acceso a datos para departamentos, roles y empleados
class DepartmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self, skip: int = 0, limit: int = 20) -> list[Department]:
        stmt = select(Department).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, department_id: UUID) -> Department | None:
        stmt = select(Department).where(Department.id == department_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Department | None:
        stmt = select(Department).where(Department.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, department: Department) -> Department:
        self.db.add(department)
        await self.db.flush()
        await self.db.refresh(department)
        return department

    async def update(self, department: Department) -> Department:
        await self.db.flush()
        await self.db.refresh(department)
        return department

    async def delete(self, department_id: UUID) -> None:
        stmt = delete(Department).where(Department.id == department_id)
        await self.db.execute(stmt)
        await self.db.flush()


class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self, skip: int = 0, limit: int = 20) -> list[Role]:
        stmt = select(Role).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, role_id: UUID) -> Role | None:
        stmt = select(Role).where(Role.id == role_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Role | None:
        stmt = select(Role).where(Role.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, role: Role) -> Role:
        self.db.add(role)
        await self.db.flush()
        await self.db.refresh(role)
        return role

    async def update(self, role: Role) -> Role:
        await self.db.flush()
        await self.db.refresh(role)
        return role

    async def delete(self, role_id: UUID) -> None:
        stmt = delete(Role).where(Role.id == role_id)
        await self.db.execute(stmt)
        await self.db.flush()


class EmployeeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_active(self, skip: int = 0, limit: int = 20) -> list[Employee]:
        stmt = (
            select(Employee)
            .options(
                selectinload(Employee.department),
                selectinload(Employee.roles),
            )
            .where(Employee.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, employee_id: UUID) -> Employee | None:
        stmt = (
            select(Employee)
            .options(
                selectinload(Employee.department),
                selectinload(Employee.roles),
            )
            .where(and_(Employee.id == employee_id, Employee.deleted_at.is_(None)))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Employee | None:
        stmt = select(Employee).where(
            and_(Employee.email == email, Employee.deleted_at.is_(None))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def count_active(self, department_id: UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(Employee)
            .where(
                and_(
                    Employee.department_id == department_id,
                    Employee.deleted_at.is_(None),
                )
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def create(self, employee: Employee) -> Employee:
        self.db.add(employee)
        await self.db.flush()
        await self.db.refresh(employee)
        return employee

    async def update(self, employee: Employee) -> Employee:
        await self.db.flush()
        await self.db.refresh(employee)
        return employee

    async def soft_delete(self, employee: Employee) -> None:
        employee.deleted_at = datetime.now(timezone.utc)
        await self.db.flush()

    async def has_role(self, employee_id: UUID, role_id: UUID) -> bool:
        stmt = select(EmployeeRole).where(
            and_(
                EmployeeRole.employee_id == employee_id,
                EmployeeRole.role_id == role_id,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def add_role(self, employee_role: EmployeeRole) -> EmployeeRole:
        self.db.add(employee_role)
        await self.db.flush()
        await self.db.refresh(employee_role)
        return employee_role

    async def remove_role(self, employee_id: UUID, role_id: UUID) -> None:
        stmt = delete(EmployeeRole).where(
            and_(
                EmployeeRole.employee_id == employee_id,
                EmployeeRole.role_id == role_id,
            )
        )
        await self.db.execute(stmt)
        await self.db.flush()
