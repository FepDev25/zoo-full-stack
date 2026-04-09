from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, paginate
from app.modules.personnel.repository import (
    DepartmentRepository,
    EmployeeRepository,
    RoleRepository,
)
from app.modules.personnel.schemas import (
    DepartmentCreate,
    DepartmentRead,
    DepartmentUpdate,
    EmployeeCreate,
    EmployeeRoleCreate,
    EmployeeRoleRead,
    EmployeeUpdate,
    EmployeeWithRolesRead,
    RoleCreate,
    RoleRead,
    RoleUpdate,
)
from app.modules.personnel.service import (
    DepartmentService,
    EmployeeService,
    RoleService,
)

router = APIRouter(prefix="/personnel", tags=["Personnel"])


# departamento

@router.get("/departments", response_model=list[DepartmentRead])
async def list_departments(
    pagination: dict = Depends(paginate),
    db: AsyncSession = Depends(get_db),
):
    service = DepartmentService(DepartmentRepository(db), EmployeeRepository(db))
    return await service.list_all(**pagination)


@router.post(
    "/departments", response_model=DepartmentRead, status_code=status.HTTP_201_CREATED
)
async def create_department(data: DepartmentCreate, db: AsyncSession = Depends(get_db)):
    service = DepartmentService(DepartmentRepository(db), EmployeeRepository(db))
    return await service.create(data)


@router.get("/departments/{department_id}", response_model=DepartmentRead)
async def get_department(department_id: UUID, db: AsyncSession = Depends(get_db)):
    service = DepartmentService(DepartmentRepository(db), EmployeeRepository(db))
    return await service.get_by_id(department_id)


@router.put("/departments/{department_id}", response_model=DepartmentRead)
async def update_department(
    department_id: UUID, data: DepartmentUpdate, db: AsyncSession = Depends(get_db)
):
    service = DepartmentService(DepartmentRepository(db), EmployeeRepository(db))
    return await service.update(department_id, data)


@router.delete("/departments/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(department_id: UUID, db: AsyncSession = Depends(get_db)):
    service = DepartmentService(DepartmentRepository(db), EmployeeRepository(db))
    await service.delete(department_id)


# roles

@router.get("/roles", response_model=list[RoleRead])
async def list_roles(
    pagination: dict = Depends(paginate),
    db: AsyncSession = Depends(get_db),
):
    service = RoleService(RoleRepository(db))
    return await service.list_all(**pagination)


@router.post("/roles", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
async def create_role(data: RoleCreate, db: AsyncSession = Depends(get_db)):
    service = RoleService(RoleRepository(db))
    return await service.create(data)


@router.get("/roles/{role_id}", response_model=RoleRead)
async def get_role(role_id: UUID, db: AsyncSession = Depends(get_db)):
    service = RoleService(RoleRepository(db))
    return await service.get_by_id(role_id)


@router.put("/roles/{role_id}", response_model=RoleRead)
async def update_role(
    role_id: UUID, data: RoleUpdate, db: AsyncSession = Depends(get_db)
):
    service = RoleService(RoleRepository(db))
    return await service.update(role_id, data)


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: UUID, db: AsyncSession = Depends(get_db)):
    service = RoleService(RoleRepository(db))
    await service.delete(role_id)


# empleados

@router.get("/employees", response_model=list[EmployeeWithRolesRead])
async def list_employees(
    pagination: dict = Depends(paginate),
    db: AsyncSession = Depends(get_db),
):
    service = EmployeeService(EmployeeRepository(db), RoleRepository(db))
    return await service.list_all(**pagination)


@router.post(
    "/employees",
    response_model=EmployeeWithRolesRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_employee(data: EmployeeCreate, db: AsyncSession = Depends(get_db)):
    service = EmployeeService(EmployeeRepository(db), RoleRepository(db))
    return await service.create(data)


@router.get("/employees/{employee_id}", response_model=EmployeeWithRolesRead)
async def get_employee(employee_id: UUID, db: AsyncSession = Depends(get_db)):
    service = EmployeeService(EmployeeRepository(db), RoleRepository(db))
    return await service.get_by_id(employee_id)


@router.put("/employees/{employee_id}", response_model=EmployeeWithRolesRead)
async def update_employee(
    employee_id: UUID, data: EmployeeUpdate, db: AsyncSession = Depends(get_db)
):
    service = EmployeeService(EmployeeRepository(db), RoleRepository(db))
    return await service.update(employee_id, data)


@router.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_employee(employee_id: UUID, db: AsyncSession = Depends(get_db)):
    service = EmployeeService(EmployeeRepository(db), RoleRepository(db))
    await service.soft_delete(employee_id)


# roles de empleado

@router.post(
    "/employees/{employee_id}/roles",
    response_model=EmployeeRoleRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_role_to_employee(
    employee_id: UUID, data: EmployeeRoleCreate, db: AsyncSession = Depends(get_db)
):
    service = EmployeeService(EmployeeRepository(db), RoleRepository(db))
    return await service.add_role(employee_id, data)


@router.delete(
    "/employees/{employee_id}/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_role_from_employee(
    employee_id: UUID, role_id: UUID, db: AsyncSession = Depends(get_db)
):
    service = EmployeeService(EmployeeRepository(db), RoleRepository(db))
    await service.remove_role(employee_id, role_id)
