"""Typed HTTP input contracts; domain validation remains in SEMS services."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class LoginInput(ApiModel):
    email: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=256)


class LabInput(ApiModel):
    lab_name: str = Field(min_length=1, max_length=120)
    department_name: str = Field(min_length=1, max_length=120)
    building_name: str = Field(min_length=1, max_length=120)
    lab_type: str = Field(min_length=1, max_length=60)


class ContactInput(ApiModel):
    contact_number: str = Field(min_length=1, max_length=30)


class UserInput(ApiModel):
    lab_id: int = Field(gt=0)
    full_name: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=1, max_length=254)
    role: str = Field(min_length=1, max_length=30)
    account_status: str = Field(min_length=1, max_length=30)


class PhoneInput(ApiModel):
    phone_number: str = Field(min_length=1, max_length=30)


class CategoryInput(ApiModel):
    category_name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class ComponentInput(ApiModel):
    category_id: int = Field(gt=0)
    component_name: str = Field(min_length=1, max_length=150)
    part_number: str | None = Field(default=None, max_length=100)
    specification: str | None = Field(default=None, max_length=1000)
    unit_of_measure: str = Field(min_length=1, max_length=30)
    minimum_stock_level: int = Field(ge=0)
    manufacturer_details: str | None = Field(default=None, max_length=255)


class LocationInput(ApiModel):
    lab_id: int = Field(gt=0)
    cabinet_no: str = Field(min_length=1, max_length=50)
    shelf_no: str | None = Field(default=None, max_length=50)
    drawer_no: str | None = Field(default=None, max_length=50)
    location_type: str = Field(min_length=1, max_length=30)


class LocationUpdateInput(ApiModel):
    cabinet_no: str = Field(min_length=1, max_length=50)
    shelf_no: str | None = Field(default=None, max_length=50)
    drawer_no: str | None = Field(default=None, max_length=50)
    location_type: str = Field(min_length=1, max_length=30)


class InventoryInput(ApiModel):
    lab_id: int = Field(gt=0)
    component_id: int = Field(gt=0)
    storage_location_id: int = Field(gt=0)
    quantity_available: int = Field(ge=0)
    unit_cost: Decimal = Field(ge=0)


class RestockInput(ApiModel):
    quantity: int = Field(gt=0)


class InventoryMetadataInput(ApiModel):
    storage_location_id: int = Field(gt=0)
    unit_cost: Decimal = Field(ge=0)


class InventoryStatusInput(ApiModel):
    status: str = Field(min_length=1, max_length=30)


class RequestLineInput(ApiModel):
    component_id: int = Field(gt=0)
    quantity_requested: int = Field(gt=0)


class RequestCreateInput(ApiModel):
    requesting_lab_id: int = Field(gt=0)
    request_date: date
    required_by_date: date
    priority: str = Field(min_length=1, max_length=30)
    reason: str = Field(min_length=1, max_length=1000)
    items: list[RequestLineInput] = Field(min_length=1)


class RequestReviewLineInput(ApiModel):
    request_item_id: int = Field(gt=0)
    quantity_approved: int = Field(ge=0)
    remarks: str | None = Field(default=None, max_length=500)


class RequestReviewInput(ApiModel):
    reviews: list[RequestReviewLineInput] = Field(min_length=1)


class TransferAllocationInput(ApiModel):
    inventory_id: int = Field(gt=0)
    quantity_sent: int = Field(gt=0)
    return_due_date: date | None = None


class TransferCreateInput(ApiModel):
    request_id: int = Field(gt=0)
    source_lab_id: int = Field(gt=0)
    destination_lab_id: int = Field(gt=0)
    allocations: list[TransferAllocationInput] = Field(min_length=1)


class DispatchConditionInput(ApiModel):
    transfer_item_id: int = Field(gt=0)
    condition_on_issue: str = Field(min_length=1, max_length=255)


class TransferDispatchInput(ApiModel):
    dispatch_date: date
    items: list[DispatchConditionInput] = Field(min_length=1)


class ReceiptLineInput(ApiModel):
    transfer_item_id: int = Field(gt=0)
    quantity_received: int = Field(ge=0)
    destination_inventory_id: int | None = Field(default=None, gt=0)
    storage_location_id: int | None = Field(default=None, gt=0)


class TransferReceiptInput(ApiModel):
    receipt_date: date
    items: list[ReceiptLineInput] = Field(min_length=1)


class ReturnLineInput(ApiModel):
    transfer_item_id: int = Field(gt=0)
    destination_inventory_id: int = Field(gt=0)
    condition_on_return: str = Field(min_length=1, max_length=255)


class TransferReturnInput(ApiModel):
    return_date: date
    items: list[ReturnLineInput] = Field(min_length=1)


class DisposalInput(ApiModel):
    inventory_id: int = Field(gt=0)
    quantity_disposed: int = Field(gt=0)
    disposal_date: date
    disposal_reason: str = Field(min_length=1, max_length=500)
    disposal_method: str = Field(min_length=1, max_length=255)
    remarks: str | None = Field(default=None, max_length=1000)

