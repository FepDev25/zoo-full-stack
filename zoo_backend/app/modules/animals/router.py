from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, paginate
from app.modules.animals.repository import (
    AnimalRepository,
    AnimalTransferRepository,
    EnclosureRepository,
    SpeciesRepository,
    ZoneRepository,
)
from app.modules.animals.schemas import (
    AnimalCreate,
    AnimalTransferCreate,
    AnimalTransferRead,
    AnimalUpdate,
    AnimalWithDetailsRead,
    EnclosureCreate,
    EnclosureRead,
    EnclosureUpdate,
    SpeciesCreate,
    SpeciesRead,
    SpeciesUpdate,
    ZoneCreate,
    ZoneRead,
    ZoneUpdate,
)
from app.modules.animals.service import (
    AnimalService,
    EnclosureService,
    SpeciesService,
    ZoneService,
)
from app.modules.personnel.repository import EmployeeRepository

router = APIRouter(prefix="/animals", tags=["Animals"])


# especies
@router.get("/species", response_model=list[SpeciesRead])
async def list_species(
    pagination: dict = Depends(paginate),
    db: AsyncSession = Depends(get_db),
):
    service = SpeciesService(SpeciesRepository(db))
    return await service.list_all(**pagination)


@router.post(
    "/species", response_model=SpeciesRead, status_code=status.HTTP_201_CREATED
)
async def create_species(data: SpeciesCreate, db: AsyncSession = Depends(get_db)):
    service = SpeciesService(SpeciesRepository(db))
    return await service.create(data)


@router.get("/species/{species_id}", response_model=SpeciesRead)
async def get_species(species_id: UUID, db: AsyncSession = Depends(get_db)):
    service = SpeciesService(SpeciesRepository(db))
    return await service.get_by_id(species_id)


@router.put("/species/{species_id}", response_model=SpeciesRead)
async def update_species(
    species_id: UUID, data: SpeciesUpdate, db: AsyncSession = Depends(get_db)
):
    service = SpeciesService(SpeciesRepository(db))
    return await service.update(species_id, data)


@router.delete("/species/{species_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_species(species_id: UUID, db: AsyncSession = Depends(get_db)):
    service = SpeciesService(SpeciesRepository(db))
    await service.delete(species_id)


# zonas
@router.get("/zones", response_model=list[ZoneRead])
async def list_zones(
    pagination: dict = Depends(paginate),
    db: AsyncSession = Depends(get_db),
):
    service = ZoneService(ZoneRepository(db), EnclosureRepository(db))
    return await service.list_all(**pagination)


@router.post("/zones", response_model=ZoneRead, status_code=status.HTTP_201_CREATED)
async def create_zone(data: ZoneCreate, db: AsyncSession = Depends(get_db)):
    service = ZoneService(ZoneRepository(db), EnclosureRepository(db))
    return await service.create(data)


@router.get("/zones/{zone_id}", response_model=ZoneRead)
async def get_zone(zone_id: UUID, db: AsyncSession = Depends(get_db)):
    service = ZoneService(ZoneRepository(db), EnclosureRepository(db))
    return await service.get_by_id(zone_id)


@router.put("/zones/{zone_id}", response_model=ZoneRead)
async def update_zone(
    zone_id: UUID, data: ZoneUpdate, db: AsyncSession = Depends(get_db)
):
    service = ZoneService(ZoneRepository(db), EnclosureRepository(db))
    return await service.update(zone_id, data)


@router.delete("/zones/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_zone(zone_id: UUID, db: AsyncSession = Depends(get_db)):
    service = ZoneService(ZoneRepository(db), EnclosureRepository(db))
    await service.delete(zone_id)


# recintos
@router.get("/enclosures", response_model=list[EnclosureRead])
async def list_enclosures(
    pagination: dict = Depends(paginate),
    db: AsyncSession = Depends(get_db),
):
    service = EnclosureService(EnclosureRepository(db), AnimalRepository(db))
    return await service.list_all(**pagination)


@router.post(
    "/enclosures", response_model=EnclosureRead, status_code=status.HTTP_201_CREATED
)
async def create_enclosure(data: EnclosureCreate, db: AsyncSession = Depends(get_db)):
    service = EnclosureService(EnclosureRepository(db), AnimalRepository(db))
    return await service.create(data)


@router.get("/enclosures/{enclosure_id}", response_model=EnclosureRead)
async def get_enclosure(enclosure_id: UUID, db: AsyncSession = Depends(get_db)):
    service = EnclosureService(EnclosureRepository(db), AnimalRepository(db))
    return await service.get_by_id(enclosure_id)


@router.put("/enclosures/{enclosure_id}", response_model=EnclosureRead)
async def update_enclosure(
    enclosure_id: UUID, data: EnclosureUpdate, db: AsyncSession = Depends(get_db)
):
    service = EnclosureService(EnclosureRepository(db), AnimalRepository(db))
    return await service.update(enclosure_id, data)


@router.delete("/enclosures/{enclosure_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enclosure(enclosure_id: UUID, db: AsyncSession = Depends(get_db)):
    service = EnclosureService(EnclosureRepository(db), AnimalRepository(db))
    await service.delete(enclosure_id)


# animales
@router.get("/", response_model=list[AnimalWithDetailsRead])
async def list_animals(
    pagination: dict = Depends(paginate),
    db: AsyncSession = Depends(get_db),
):
    service = AnimalService(
        AnimalRepository(db),
        SpeciesRepository(db),
        EnclosureRepository(db),
        AnimalTransferRepository(db),
    )
    return await service.list_all(**pagination)


@router.post(
    "/", response_model=AnimalWithDetailsRead, status_code=status.HTTP_201_CREATED
)
async def create_animal(data: AnimalCreate, db: AsyncSession = Depends(get_db)):
    service = AnimalService(
        AnimalRepository(db),
        SpeciesRepository(db),
        EnclosureRepository(db),
        AnimalTransferRepository(db),
    )
    return await service.create(data)


@router.get("/{animal_id}", response_model=AnimalWithDetailsRead)
async def get_animal(animal_id: UUID, db: AsyncSession = Depends(get_db)):
    service = AnimalService(
        AnimalRepository(db),
        SpeciesRepository(db),
        EnclosureRepository(db),
        AnimalTransferRepository(db),
    )
    return await service.get_by_id(animal_id)


@router.put("/{animal_id}", response_model=AnimalWithDetailsRead)
async def update_animal(
    animal_id: UUID, data: AnimalUpdate, db: AsyncSession = Depends(get_db)
):
    service = AnimalService(
        AnimalRepository(db),
        SpeciesRepository(db),
        EnclosureRepository(db),
        AnimalTransferRepository(db),
    )
    return await service.update(animal_id, data)


@router.delete("/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_animal(animal_id: UUID, db: AsyncSession = Depends(get_db)):
    service = AnimalService(
        AnimalRepository(db),
        SpeciesRepository(db),
        EnclosureRepository(db),
        AnimalTransferRepository(db),
    )
    await service.soft_delete(animal_id)


# transferencias de animales
@router.get("/{animal_id}/transfers", response_model=list[AnimalTransferRead])
async def list_animal_transfers(
    animal_id: UUID,
    pagination: dict = Depends(paginate),
    db: AsyncSession = Depends(get_db),
):
    service = AnimalService(
        AnimalRepository(db),
        SpeciesRepository(db),
        EnclosureRepository(db),
        AnimalTransferRepository(db),
    )
    return await service.list_transfers(animal_id, **pagination)


@router.post(
    "/transfers", response_model=AnimalTransferRead, status_code=status.HTTP_201_CREATED
)
async def create_transfer(
    data: AnimalTransferCreate, db: AsyncSession = Depends(get_db)
):
    service = AnimalService(
        AnimalRepository(db),
        SpeciesRepository(db),
        EnclosureRepository(db),
        AnimalTransferRepository(db),
    )
    return await service.create_transfer(data, EmployeeRepository(db))


@router.get("/transfers/{transfer_id}", response_model=AnimalTransferRead)
async def get_transfer(transfer_id: UUID, db: AsyncSession = Depends(get_db)):
    service = AnimalService(
        AnimalRepository(db),
        SpeciesRepository(db),
        EnclosureRepository(db),
        AnimalTransferRepository(db),
    )
    return await service.get_transfer_by_id(transfer_id)
