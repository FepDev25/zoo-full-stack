import enum
import re
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from uuid import UUID


# enumeraciones


class DepartmentStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class EmployeeStatus(str, enum.Enum):
    active = "active"
    on_leave = "on_leave"
    inactive = "inactive"


# esquemas de departamento

class DepartmentBase(BaseModel):
    name: str
    description: str | None = None
    status: DepartmentStatus = DepartmentStatus.active


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: DepartmentStatus | None = None


class DepartmentRead(DepartmentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


# esquemas de rol

class RoleBase(BaseModel):
    name: str
    description: str | None = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class RoleRead(RoleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


# esquemas de rol de empleado


class EmployeeRoleCreate(BaseModel):
    role_id: UUID


class EmployeeRoleRead(BaseModel):
    id: UUID
    employee_id: UUID
    role_id: UUID
    assigned_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoleSimple(BaseModel):
    id: UUID
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


# esquemas de empleado

class EmployeeBase(BaseModel):
    full_name: str
    email: str
    phone: str | None = None
    hire_date: date
    birth_date: date | None = None
    department_id: UUID
    status: EmployeeStatus = EmployeeStatus.active

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is not None and not re.match(r"^\+?[0-9]{7,15}$", v):
            raise ValueError("Phone must match pattern: + followed by 7 to 15 digits")
        return v

    @field_validator("hire_date")
    @classmethod
    def validate_hire_date(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("hire_date cannot be in the future")
        return v

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: date | None) -> date | None:
        if v is not None and v > date.today():
            raise ValueError("birth_date cannot be in the future")
        return v

    @model_validator(mode="after")
    def validate_birth_before_hire(self) -> "EmployeeBase":
        if self.birth_date is not None and self.hire_date is not None:
            if self.birth_date >= self.hire_date:
                raise ValueError("birth_date must be before hire_date")
        return self


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    hire_date: date | None = None
    birth_date: date | None = None
    department_id: UUID | None = None
    status: EmployeeStatus | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is not None and not re.match(r"^\+?[0-9]{7,15}$", v):
            raise ValueError("Phone must match pattern: + followed by 7 to 15 digits")
        return v

    @field_validator("hire_date")
    @classmethod
    def validate_hire_date(cls, v: date | None) -> date | None:
        if v is not None and v > date.today():
            raise ValueError("hire_date cannot be in the future")
        return v

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: date | None) -> date | None:
        if v is not None and v > date.today():
            raise ValueError("birth_date cannot be in the future")
        return v

    @model_validator(mode="after")
    def validate_birth_before_hire(self) -> "EmployeeUpdate":
        if self.birth_date is not None and self.hire_date is not None:
            if self.birth_date >= self.hire_date:
                raise ValueError("birth_date must be before hire_date")
        return self


class EmployeeRead(EmployeeBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class EmployeeWithRolesRead(EmployeeRead):
    roles: list[RoleSimple] = []
