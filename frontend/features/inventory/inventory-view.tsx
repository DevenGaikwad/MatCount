"use client";

import { useMemo, useState } from "react";
import { Icon } from "@/components/icon";
import { useToast } from "@/components/toast";
import { Button } from "@/components/ui/button";
import { AccessNotice } from "@/components/ui/access-notice";
import { Panel } from "@/components/ui/card";
import { DataTable } from "@/components/ui/data-table";
import { Dialog } from "@/components/ui/dialog";
import { Field, Input, Select } from "@/components/ui/fields";
import { PageHeader, SectionHeader } from "@/components/ui/page";
import { ErrorState, LoadingState } from "@/components/ui/states";
import { ApiError, apiRequest } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { can } from "@/lib/permissions";
import { useApiData } from "@/lib/use-api-data";
import type { DataRow } from "@/types/api";

const availabilityColumns = [
  { key: "component_name", label: "Component" },
  { key: "part_number", label: "Part Number" },
  { key: "category_name", label: "Category" },
  { key: "lab_name", label: "Laboratory" },
  { key: "quantity_available", label: "Available", numeric: true },
  { key: "inventory_status", label: "Status" },
];
const operationalColumns = [
  { key: "inventory_id", label: "Position", numeric: true },
  { key: "cabinet_no", label: "Cabinet" },
  { key: "quantity_reserved", label: "Reserved", numeric: true },
];
const financialColumns = [
  { key: "unit_cost", label: "Unit Cost", numeric: true },
  { key: "inventory_value", label: "On-Hand Value", numeric: true },
];
type Action = "create" | "restock" | "metadata" | "status" | null;

export function InventoryView() {
  const { actor, token } = useAuth(); const { showToast } = useToast();
  const staff = actor ? can(actor.role, "MANAGE_INVENTORY") : false;
  const operational = actor ? can(actor.role, "VIEW_INVENTORY_COORDINATES") : false;
  const financial = actor ? can(actor.role, "VIEW_FINANCIAL_FIELDS") : false;
  const inventoryState = useApiData<DataRow[]>("/inventory");
  const labsState = useApiData<DataRow[]>("/labs"); const componentsState = useApiData<DataRow[]>("/components");
  const locationsState = useApiData<DataRow[]>("/storage-locations", staff);
  const [selected, setSelected] = useState<DataRow | null>(null); const [action, setAction] = useState<Action>(null);
  const [labFilter, setLabFilter] = useState("ALL"); const [statusFilter, setStatusFilter] = useState("ALL");
  const [createLab, setCreateLab] = useState(actor ? String(actor.lab_id) : "");
  const [busy, setBusy] = useState(false); const [formError, setFormError] = useState("");
  const columns = useMemo(
    () => [
      ...(operational ? operationalColumns.slice(0, 1) : []),
      ...availabilityColumns.slice(0, 4),
      ...(operational ? operationalColumns.slice(1, 2) : []),
      ...availabilityColumns.slice(4, 5),
      ...(operational ? operationalColumns.slice(2) : []),
      ...(financial ? financialColumns : []),
      ...availabilityColumns.slice(5),
    ],
    [financial, operational],
  );
  const permittedLabs = useMemo(() => actor?.role === "ADMINISTRATOR" ? labsState.data ?? [] : (labsState.data ?? []).filter((lab) => Number(lab.lab_id) === actor?.lab_id), [actor, labsState.data]);
  const filtered = useMemo(() => (inventoryState.data ?? []).filter((row) => (labFilter === "ALL" || String(row.lab_id) === labFilter) && (statusFilter === "ALL" || String(row.inventory_status) === statusFilter)), [inventoryState.data, labFilter, statusFilter]);
  const locations = locationsState.data ?? [];
  const locationsForCreate = locations.filter((row) => String(row.lab_id) === createLab);
  const locationsForSelected = locations.filter((row) => String(row.lab_id) === String(selected?.lab_id));
  const accessMessage = actor?.role === "STUDENT"
    ? { title: "Availability-only academic view", description: "Storage coordinates, reservations, unit costs and valuations are withheld by the API." }
    : actor?.role === "FACULTY"
      ? { title: "Faculty operational view", description: "Stock and location context is available; financial fields remain restricted." }
      : actor?.role === "LAB_ASSISTANT"
        ? { title: "Own-laboratory operational view", description: "Cost fields are available only for stock duties within your assigned laboratory." }
        : { title: "Department-wide administrative view", description: "Cross-laboratory stock and valuation fields are available for authorized oversight." };

  async function save(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!token || !action) return;
    const values = Object.fromEntries(new FormData(event.currentTarget));
    let path = "/inventory"; let method = "POST";
    if (selected && action !== "create") path = `/inventory/${selected.inventory_id}/${action}`;
    if (action === "metadata" || action === "status") method = "PATCH";
    setBusy(true); setFormError("");
    try { const response = await apiRequest<DataRow>(path, { method, body: JSON.stringify(values) }, token); showToast(response.message ?? "Inventory updated."); setAction(null); setSelected(null); await inventoryState.refresh(); }
    catch (caught) { setFormError(caught instanceof ApiError ? caught.message : "Inventory operation could not be completed."); } finally { setBusy(false); }
  }

  if (inventoryState.loading || labsState.loading || componentsState.loading || (staff && locationsState.loading)) return <LoadingState label="Loading laboratory inventory…" />;
  const combinedError = inventoryState.error || labsState.error || componentsState.error || (staff ? locationsState.error : "");
  if (combinedError || !inventoryState.data || !labsState.data || !componentsState.data || (staff && !locationsState.data)) return <ErrorState message={combinedError || "Inventory data is unavailable."} onRetry={() => { void inventoryState.refresh(); void labsState.refresh(); void componentsState.refresh(); if (staff) void locationsState.refresh(); }} />;
  return (
    <>
      <PageHeader eyebrow="Stock control" title="Inventory" description={actor?.role === "STUDENT" ? "Find components and compare permitted availability across laboratories." : "Search physical component positions and monitor role-authorized operational stock."} actions={staff ? <Button onClick={() => { setSelected(null); setCreateLab(String(permittedLabs[0]?.lab_id ?? actor?.lab_id ?? "")); setAction("create"); }}><Icon name="plus" size={17} />Register Inventory</Button> : undefined} />
      <AccessNotice title={accessMessage.title} description={accessMessage.description} />
      <Panel>
        <SectionHeader title="Inventory positions" description={financial ? "On-hand value includes available and reserved stock still physically held." : "Results are projected by the API according to your role and laboratory scope."} />
        <div className="filter-bar">
          <Field label="Laboratory" htmlFor="inventory_lab"><Select id="inventory_lab" value={labFilter} onChange={(event) => { setLabFilter(event.target.value); setSelected(null); }}><option value="ALL">All laboratories</option>{labsState.data.map((lab) => <option key={String(lab.lab_id)} value={String(lab.lab_id)}>{String(lab.lab_name)}</option>)}</Select></Field>
          <Field label="Status" htmlFor="inventory_status_filter"><Select id="inventory_status_filter" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}><option value="ALL">All statuses</option>{["AVAILABLE", "LOW_STOCK", "OUT_OF_STOCK", "BLOCKED", "INACTIVE"].map((status) => <option key={status}>{status.replaceAll("_", " ")}</option>)}</Select></Field>
        </div>
        <DataTable rows={filtered} columns={columns} idKey="inventory_id" selectedId={selected?.inventory_id} onRowClick={setSelected} searchPlaceholder="Search component, part number, lab or location" emptyTitle="No inventory positions" emptyDescription="No stock position matches the current filters." />
      </Panel>
      {selected ? <Panel><SectionHeader title={`${selected.component_name}${selected.inventory_id ? ` · Position ${selected.inventory_id}` : ""}`} description={selected.cabinet_no ? `${selected.lab_name} · Cabinet ${selected.cabinet_no} / ${selected.shelf_no || "—"} / ${selected.drawer_no || "—"}` : String(selected.lab_name)} action={staff ? <div className="page-actions"><Button variant="secondary" onClick={() => setAction("restock")}>Add Stock</Button><Button variant="secondary" onClick={() => setAction("metadata")}>Move / Cost</Button><Button variant="secondary" onClick={() => setAction("status")}>Set Status</Button></div> : undefined} /><div className="detail-grid"><div className="detail-item"><span>Available</span><strong>{String(selected.quantity_available)}</strong></div>{"quantity_reserved" in selected ? <div className="detail-item"><span>Reserved</span><strong>{String(selected.quantity_reserved)}</strong></div> : null}{"quantity_accounted" in selected ? <div className="detail-item"><span>Accounted stock</span><strong>{String(selected.quantity_accounted)}</strong></div> : null}</div></Panel> : null}
      <Dialog open={action !== null} onClose={() => setAction(null)} title={action === "create" ? "Register inventory position" : action === "restock" ? "Add available stock" : action === "metadata" ? "Move position or update cost" : "Set operational status"} description="Every stock-changing action is revalidated and committed by the Python service layer.">
        <form className="form-grid" onSubmit={save}>
          {action === "create" ? <>
            <Field label="Laboratory" htmlFor="new_lab" required><Select id="new_lab" name="lab_id" value={createLab} onChange={(event) => setCreateLab(event.target.value)} required>{permittedLabs.map((lab) => <option key={String(lab.lab_id)} value={String(lab.lab_id)}>{String(lab.lab_name)}</option>)}</Select></Field>
            <Field label="Component" htmlFor="component_id" required><Select id="component_id" name="component_id" required><option value="">Select component</option>{componentsState.data.map((component) => <option key={String(component.component_id)} value={String(component.component_id)}>{String(component.component_name)}{component.part_number ? ` · ${component.part_number}` : ""}</option>)}</Select></Field>
            <Field label="Storage location" htmlFor="storage_location_id" required><Select id="storage_location_id" name="storage_location_id" required><option value="">Select location</option>{locationsForCreate.map((location) => <option key={String(location.storage_location_id)} value={String(location.storage_location_id)}>Cabinet {String(location.cabinet_no)} / {String(location.shelf_no || "—")} / {String(location.drawer_no || "—")}</option>)}</Select></Field>
            <Field label="Available quantity" htmlFor="quantity_available" required><Input id="quantity_available" name="quantity_available" type="number" min="0" defaultValue="0" required /></Field>
            <Field label="Unit cost (₹)" htmlFor="unit_cost" required><Input id="unit_cost" name="unit_cost" type="number" min="0" step="0.01" defaultValue="0.00" required /></Field>
          </> : null}
          {action === "restock" ? <Field label="Restock quantity" htmlFor="quantity" required><Input id="quantity" name="quantity" type="number" min="1" defaultValue="1" required /></Field> : null}
          {action === "metadata" ? <><Field label="Storage location" htmlFor="metadata_location" required><Select id="metadata_location" name="storage_location_id" defaultValue={String(selected?.storage_location_id ?? "")} required>{locationsForSelected.map((location) => <option key={String(location.storage_location_id)} value={String(location.storage_location_id)}>Cabinet {String(location.cabinet_no)} / {String(location.shelf_no || "—")} / {String(location.drawer_no || "—")}</option>)}</Select></Field><Field label="Unit cost (₹)" htmlFor="metadata_cost" required><Input id="metadata_cost" name="unit_cost" type="number" min="0" step="0.01" defaultValue={String(selected?.unit_cost ?? 0)} required /></Field></> : null}
          {action === "status" ? <Field label="Operational status" htmlFor="status" required><Select id="status" name="status" defaultValue="AVAILABLE">{["AVAILABLE", "BLOCKED", "INACTIVE"].map((status) => <option key={status}>{status}</option>)}</Select></Field> : null}
          {formError ? <div className="inline-error full"><Icon name="alert" size={18} />{formError}</div> : null}<div className="form-actions"><Button type="button" variant="secondary" onClick={() => setAction(null)}>Cancel</Button><Button type="submit" busy={busy}>{action === "create" ? "Register Inventory" : action === "restock" ? "Add Stock" : action === "metadata" ? "Save Inventory Metadata" : "Set Status"}</Button></div>
        </form>
      </Dialog>
    </>
  );
}
