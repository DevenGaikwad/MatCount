"""Validated role-aware master-data operations."""

from __future__ import annotations

from sqlalchemy.exc import IntegrityError

from config.constants import AccountStatus, Role
from db.session import session_scope
from repositories import component_repository, lab_repository, user_repository
from services.exceptions import NotFoundError, ValidationError
from services.rbac import Actor, revalidate_actor, require_lab_scope, require_roles
from services.validation import (
    email_address,
    nonnegative_int,
    optional_text,
    phone_number,
    positive_int,
    required_text,
)


def list_labs(search: str | None = None):
    with session_scope() as session:
        return lab_repository.list_labs(session, search)


def create_lab(
    actor: Actor,
    *,
    lab_name: str,
    department_name: str,
    building_name: str,
    lab_type: str,
):
    require_roles(actor, [Role.ADMINISTRATOR])
    try:
        with session_scope() as session:
            revalidate_actor(session, actor)
            return lab_repository.create_lab(
                session,
                lab_name=required_text(lab_name, "Laboratory name", max_length=120),
                department_name=required_text(
                    department_name, "Department", max_length=120
                ),
                building_name=required_text(building_name, "Building", max_length=120),
                lab_type=required_text(lab_type, "Laboratory type", max_length=60),
            )
    except IntegrityError:
        raise ValidationError(
            "A laboratory with this name and department already exists."
        ) from None


def update_lab(actor: Actor, lab_id: int, **changes: str):
    require_roles(actor, [Role.ADMINISTRATOR])
    lab_id = positive_int(lab_id, "Laboratory ID")
    allowed = {"lab_name", "department_name", "building_name", "lab_type"}
    try:
        with session_scope() as session:
            revalidate_actor(session, actor)
            record = lab_repository.get_lab(session, lab_id)
            if record is None:
                raise NotFoundError("Laboratory not found.")
            for key, value in changes.items():
                if key in allowed and value is not None:
                    maximum = 60 if key == "lab_type" else 120
                    setattr(
                        record,
                        key,
                        required_text(
                            value, key.replace("_", " ").title(), max_length=maximum
                        ),
                    )
            session.flush()
            return record
    except IntegrityError:
        raise ValidationError("The laboratory update conflicts with existing data.") from None


def list_lab_contacts(actor: Actor, lab_id: int):
    require_roles(actor, [Role.ADMINISTRATOR])
    lab_id = positive_int(lab_id, "Laboratory ID")
    with session_scope() as session:
        revalidate_actor(session, actor)
        if lab_repository.get_lab(session, lab_id) is None:
            raise NotFoundError("Laboratory not found.")
        return lab_repository.list_contacts(session, lab_id)


def add_lab_contact(actor: Actor, lab_id: int, contact_number: str):
    require_roles(actor, [Role.ADMINISTRATOR])
    lab_id = positive_int(lab_id, "Laboratory ID")
    try:
        with session_scope() as session:
            revalidate_actor(session, actor)
            if lab_repository.get_lab(session, lab_id) is None:
                raise NotFoundError("Laboratory not found.")
            return lab_repository.add_contact(
                session, lab_id, phone_number(contact_number, "Laboratory contact")
            )
    except IntegrityError:
        raise ValidationError("This laboratory contact is already recorded.") from None


def list_users(actor: Actor, *, lab_id: int | None = None, search: str | None = None):
    require_roles(actor, [Role.ADMINISTRATOR])
    if lab_id is not None:
        lab_id = positive_int(lab_id, "Laboratory ID")
    with session_scope() as session:
        revalidate_actor(session, actor)
        return user_repository.list_users(session, lab_id=lab_id, search=search)


def create_user(
    actor: Actor,
    *,
    lab_id: int,
    full_name: str,
    email: str,
    role: str,
    account_status: str = AccountStatus.ACTIVE.value,
):
    require_roles(actor, [Role.ADMINISTRATOR])
    lab_id = positive_int(lab_id, "Laboratory ID")
    if role not in {item.value for item in Role}:
        raise ValidationError("Invalid SEMS role.")
    if account_status not in {item.value for item in AccountStatus}:
        raise ValidationError("Invalid account status.")
    try:
        with session_scope() as session:
            revalidate_actor(session, actor)
            if lab_repository.get_lab(session, lab_id) is None:
                raise NotFoundError("Assigned laboratory not found.")
            return user_repository.create_user(
                session,
                lab_id=lab_id,
                full_name=required_text(full_name, "Full name", max_length=150),
                email=email_address(email),
                role=role,
                account_status=account_status,
            )
    except IntegrityError:
        raise ValidationError("The email is already registered in SEMS.") from None


def update_user(actor: Actor, user_id: int, **changes: object):
    require_roles(actor, [Role.ADMINISTRATOR])
    user_id = positive_int(user_id, "User ID")
    allowed = {"lab_id", "full_name", "email", "role", "account_status"}
    with session_scope() as session:
        revalidate_actor(session, actor)
        record = user_repository.get_user(session, user_id)
        if record is None:
            raise NotFoundError("User not found.")
        for key, value in changes.items():
            if key not in allowed or value is None:
                continue
            if key in {"full_name", "email"}:
                value = (
                    email_address(value)
                    if key == "email"
                    else required_text(value, "Full name", max_length=150)
                )
            if key == "lab_id":
                value = positive_int(value, "Laboratory ID")
                if lab_repository.get_lab(session, value) is None:
                    raise NotFoundError("Assigned laboratory not found.")
            if key == "role" and str(value) not in {item.value for item in Role}:
                raise ValidationError("Invalid SEMS role.")
            if key == "account_status" and str(value) not in {
                item.value for item in AccountStatus
            }:
                raise ValidationError("Invalid account status.")
            setattr(record, key, value)
        try:
            session.flush()
        except IntegrityError:
            raise ValidationError("The user update conflicts with existing data.") from None
        return record


def list_user_phones(actor: Actor, user_id: int):
    require_roles(actor, [Role.ADMINISTRATOR])
    user_id = positive_int(user_id, "User ID")
    with session_scope() as session:
        revalidate_actor(session, actor)
        if user_repository.get_user(session, user_id) is None:
            raise NotFoundError("User not found.")
        return user_repository.list_phones(session, user_id)


def add_user_phone(actor: Actor, user_id: int, number: str):
    require_roles(actor, [Role.ADMINISTRATOR])
    user_id = positive_int(user_id, "User ID")
    try:
        with session_scope() as session:
            revalidate_actor(session, actor)
            if user_repository.get_user(session, user_id) is None:
                raise NotFoundError("User not found.")
            return user_repository.add_phone(
                session, user_id, phone_number(number, "User phone number")
            )
    except IntegrityError:
        raise ValidationError("This phone number is already recorded for the user.") from None


def list_categories():
    with session_scope() as session:
        return component_repository.list_categories(session)


def create_category(actor: Actor, *, category_name: str, description: str | None = None):
    require_roles(actor, [Role.ADMINISTRATOR])
    try:
        with session_scope() as session:
            revalidate_actor(session, actor)
            return component_repository.create_category(
                session,
                category_name=required_text(
                    category_name, "Category name", max_length=100
                ),
                description=optional_text(
                    description, "Category description", max_length=500
                ),
            )
    except IntegrityError:
        raise ValidationError("This component category already exists.") from None


def list_components(*, category_id: int | None = None, search: str | None = None):
    if category_id is not None:
        category_id = positive_int(category_id, "Category ID")
    with session_scope() as session:
        return component_repository.list_components(
            session, category_id=category_id, search=search
        )


def create_component(
    actor: Actor,
    *,
    category_id: int,
    component_name: str,
    part_number: str | None,
    specification: str | None,
    unit_of_measure: str,
    minimum_stock_level: int,
    manufacturer_details: str | None,
):
    require_roles(actor, [Role.ADMINISTRATOR])
    category_id = positive_int(category_id, "Category ID")
    minimum_stock_level = nonnegative_int(
        minimum_stock_level, "Minimum stock level"
    )
    try:
        with session_scope() as session:
            revalidate_actor(session, actor)
            if component_repository.get_category(session, category_id) is None:
                raise NotFoundError("Component category not found.")
            return component_repository.create_component(
                session,
                category_id=category_id,
                component_name=required_text(
                    component_name, "Component name", max_length=160
                ),
                part_number=optional_text(part_number, "Part number", max_length=120),
                specification=optional_text(
                    specification, "Specification", max_length=16000
                ),
                unit_of_measure=required_text(
                    unit_of_measure, "Unit of measure", max_length=30
                ),
                minimum_stock_level=minimum_stock_level,
                manufacturer_details=optional_text(
                    manufacturer_details, "Manufacturer details", max_length=255
                ),
            )
    except IntegrityError:
        raise ValidationError(
            "The part number already exists or the category is invalid."
        ) from None


def update_component(actor: Actor, component_id: int, **changes: object):
    require_roles(actor, [Role.ADMINISTRATOR])
    component_id = positive_int(component_id, "Component ID")
    allowed = {
        "category_id",
        "component_name",
        "part_number",
        "specification",
        "unit_of_measure",
        "minimum_stock_level",
        "manufacturer_details",
    }
    with session_scope() as session:
        revalidate_actor(session, actor)
        record = component_repository.get_component(session, component_id)
        if record is None:
            raise NotFoundError("Component not found.")
        for key, value in changes.items():
            if key not in allowed:
                continue
            if key == "minimum_stock_level":
                value = nonnegative_int(value, "Minimum stock level")
            if key == "category_id":
                value = positive_int(value, "Category ID")
                if component_repository.get_category(session, value) is None:
                    raise NotFoundError("Component category not found.")
            if key in {"component_name", "unit_of_measure"}:
                maximum = 160 if key == "component_name" else 30
                value = required_text(
                    value, key.replace("_", " ").title(), max_length=maximum
                )
            if key in {"part_number", "specification", "manufacturer_details"}:
                if key == "specification":
                    value = optional_text(value, "Specification", max_length=16000)
                else:
                    maximum = 120 if key == "part_number" else 255
                    value = optional_text(
                        value, key.replace("_", " ").title(), max_length=maximum
                    )
            setattr(record, key, value)
        try:
            session.flush()
        except IntegrityError:
            raise ValidationError("The component update conflicts with existing data.") from None
        return record


def list_locations(actor: Actor, *, lab_id: int | None = None):
    require_roles(actor, [Role.LAB_ASSISTANT, Role.ADMINISTRATOR])
    if actor.role != Role.ADMINISTRATOR.value:
        lab_id = actor.lab_id
    elif lab_id is not None:
        lab_id = positive_int(lab_id, "Laboratory ID")
    with session_scope() as session:
        revalidate_actor(session, actor)
        return lab_repository.list_locations(session, lab_id)


def create_location(
    actor: Actor,
    *,
    lab_id: int,
    cabinet_no: str,
    shelf_no: str | None,
    drawer_no: str | None,
    location_type: str,
):
    require_roles(actor, [Role.LAB_ASSISTANT, Role.ADMINISTRATOR])
    lab_id = positive_int(lab_id, "Laboratory ID")
    require_lab_scope(actor, lab_id)
    cleaned = {
        "cabinet_no": required_text(cabinet_no, "Cabinet number", max_length=30),
        "shelf_no": optional_text(shelf_no, "Shelf number", max_length=30),
        "drawer_no": optional_text(drawer_no, "Drawer number", max_length=30),
        "location_type": required_text(
            location_type, "Location type", max_length=50
        ).upper(),
    }
    try:
        with session_scope() as session:
            revalidate_actor(session, actor)
            if lab_repository.get_lab(session, lab_id) is None:
                raise NotFoundError("Laboratory not found.")
            duplicate = lab_repository.find_null_normalized_location(
                session, lab_id=lab_id, **cleaned
            )
            if duplicate:
                raise ValidationError("This storage coordinate already exists.")
            return lab_repository.create_location(session, lab_id=lab_id, **cleaned)
    except IntegrityError:
        raise ValidationError(
            "This storage coordinate was created concurrently; refresh and retry."
        ) from None


def update_location(
    actor: Actor,
    storage_location_id: int,
    *,
    cabinet_no: str,
    shelf_no: str | None,
    drawer_no: str | None,
    location_type: str,
):
    require_roles(actor, [Role.LAB_ASSISTANT, Role.ADMINISTRATOR])
    storage_location_id = positive_int(
        storage_location_id, "Storage-location ID"
    )
    cleaned = {
        "cabinet_no": required_text(cabinet_no, "Cabinet number", max_length=30),
        "shelf_no": optional_text(shelf_no, "Shelf number", max_length=30),
        "drawer_no": optional_text(drawer_no, "Drawer number", max_length=30),
        "location_type": required_text(
            location_type, "Location type", max_length=50
        ).upper(),
    }
    try:
        with session_scope() as session:
            revalidate_actor(session, actor)
            record = lab_repository.get_location(
                session, storage_location_id, for_update=True
            )
            if record is None:
                raise NotFoundError("Storage location not found.")
            require_lab_scope(actor, record.lab_id)
            duplicate = lab_repository.find_null_normalized_location(
                session,
                lab_id=record.lab_id,
                exclude_id=record.storage_location_id,
                **cleaned,
            )
            if duplicate:
                raise ValidationError("This storage coordinate already exists.")
            for key, value in cleaned.items():
                setattr(record, key, value)
            session.flush()
            return record
    except IntegrityError:
        raise ValidationError(
            "This storage coordinate conflicts with an existing location."
        ) from None
