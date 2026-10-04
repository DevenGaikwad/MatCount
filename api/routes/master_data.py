"""Laboratory, user, catalogue and storage HTTP adapters."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from api.dependencies import current_actor
from api.schemas import (
    CategoryInput,
    ComponentInput,
    ContactInput,
    LabInput,
    LocationInput,
    LocationUpdateInput,
    PhoneInput,
    UserInput,
)
from api.serialization import success
from services import master_data_service
from services.rbac import Actor


router = APIRouter(tags=["Master Data"])


@router.get("/labs")
def list_labs(
    search: str | None = Query(default=None, max_length=120),
    _actor: Actor = Depends(current_actor),
):
    return success(master_data_service.list_labs(search or None))


@router.post("/labs")
def create_lab(payload: LabInput, actor: Actor = Depends(current_actor)):
    record = master_data_service.create_lab(actor, **payload.model_dump())
    return success(record, message="Laboratory created.")


@router.patch("/labs/{lab_id}")
def update_lab(lab_id: int, payload: LabInput, actor: Actor = Depends(current_actor)):
    record = master_data_service.update_lab(actor, lab_id, **payload.model_dump())
    return success(record, message="Laboratory updated.")


@router.get("/labs/{lab_id}/contacts")
def list_contacts(lab_id: int, actor: Actor = Depends(current_actor)):
    return success(master_data_service.list_lab_contacts(actor, lab_id))


@router.post("/labs/{lab_id}/contacts")
def add_contact(
    lab_id: int, payload: ContactInput, actor: Actor = Depends(current_actor)
):
    record = master_data_service.add_lab_contact(
        actor, lab_id, payload.contact_number
    )
    return success(record, message="Laboratory contact added.")


@router.get("/users")
def list_users(
    lab_id: int | None = Query(default=None, gt=0),
    search: str | None = Query(default=None, max_length=254),
    actor: Actor = Depends(current_actor),
):
    return success(
        master_data_service.list_users(actor, lab_id=lab_id, search=search or None)
    )


@router.post("/users")
def create_user(payload: UserInput, actor: Actor = Depends(current_actor)):
    record = master_data_service.create_user(actor, **payload.model_dump())
    return success(
        record,
        message="User created. Configure external credentials separately if required.",
    )


@router.patch("/users/{user_id}")
def update_user(
    user_id: int, payload: UserInput, actor: Actor = Depends(current_actor)
):
    record = master_data_service.update_user(actor, user_id, **payload.model_dump())
    return success(record, message="User updated.")


@router.get("/users/{user_id}/phones")
def list_phones(user_id: int, actor: Actor = Depends(current_actor)):
    return success(master_data_service.list_user_phones(actor, user_id))


@router.post("/users/{user_id}/phones")
def add_phone(user_id: int, payload: PhoneInput, actor: Actor = Depends(current_actor)):
    record = master_data_service.add_user_phone(
        actor, user_id, payload.phone_number
    )
    return success(record, message="User phone number added.")


@router.get("/categories")
def list_categories(_actor: Actor = Depends(current_actor)):
    return success(master_data_service.list_categories())


@router.post("/categories")
def create_category(payload: CategoryInput, actor: Actor = Depends(current_actor)):
    record = master_data_service.create_category(actor, **payload.model_dump())
    return success(record, message="Component category created.")


@router.get("/components")
def list_components(
    category_id: int | None = Query(default=None, gt=0),
    search: str | None = Query(default=None, max_length=255),
    _actor: Actor = Depends(current_actor),
):
    return success(
        master_data_service.list_components(
            category_id=category_id, search=search or None
        )
    )


@router.post("/components")
def create_component(
    payload: ComponentInput, actor: Actor = Depends(current_actor)
):
    record = master_data_service.create_component(actor, **payload.model_dump())
    return success(record, message="Component created.")


@router.patch("/components/{component_id}")
def update_component(
    component_id: int,
    payload: ComponentInput,
    actor: Actor = Depends(current_actor),
):
    record = master_data_service.update_component(
        actor, component_id, **payload.model_dump()
    )
    return success(record, message="Component updated.")


@router.get("/storage-locations")
def list_locations(
    lab_id: int | None = Query(default=None, gt=0),
    actor: Actor = Depends(current_actor),
):
    return success(master_data_service.list_locations(actor, lab_id=lab_id))


@router.post("/storage-locations")
def create_location(payload: LocationInput, actor: Actor = Depends(current_actor)):
    record = master_data_service.create_location(actor, **payload.model_dump())
    return success(record, message="Storage location created.")


@router.patch("/storage-locations/{storage_location_id}")
def update_location(
    storage_location_id: int,
    payload: LocationUpdateInput,
    actor: Actor = Depends(current_actor),
):
    record = master_data_service.update_location(
        actor, storage_location_id, **payload.model_dump()
    )
    return success(record, message="Storage location updated.")

