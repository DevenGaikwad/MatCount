"use client";

import { useMemo, useState } from "react";
import { Icon } from "@/components/icon";
import { useToast } from "@/components/toast";
import { Button } from "@/components/ui/button";
import { Panel } from "@/components/ui/card";
import { DataTable } from "@/components/ui/data-table";
import { Dialog } from "@/components/ui/dialog";
import { Field, Input, Select } from "@/components/ui/fields";
import { PageHeader, SectionHeader } from "@/components/ui/page";
import { ErrorState, LoadingState } from "@/components/ui/states";
import { ApiError, apiRequest } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useApiData } from "@/lib/use-api-data";
import type { DataRow } from "@/types/api";

const columns = [
  { key: "storage_location_id", label: "Location ID", numeric: true }, { key: "lab_id", label: "Lab", numeric: true },
  { key: "cabinet_no", label: "Cabinet" }, { key: "shelf_no", label: "Shelf" },
  { key: "drawer_no", label: "Drawer / Bin" }, { key: "location_type", label: "Type" },
];

export function StorageView() {
  const { actor, token } = useAuth(); const { showToast } = useToast();
  const labsState = useApiData<DataRow[]>("/labs");
  const [labId, setLabId] = useState(actor ? String(actor.lab_id) : "");
  const effectiveLabId = labId || (actor ? String(actor.lab_id) : "");
  const locationsState = useApiData<DataRow[]>(effectiveLabId ? `/storage-locations?lab_id=${effectiveLabId}` : "/storage-locations");
  const [selected, setSelected] = useState<DataRow | null>(null);
  const [dialog, setDialog] = useState<"create" | "edit" | null>(null);
  const [busy, setBusy] = useState(false); const [formError, setFormError] = useState("");

  const permittedLabs = useMemo(() => actor?.role === "ADMINISTRATOR" ? labsState.data ?? [] : (labsState.data ?? []).filter((lab) => Number(lab.lab_id) === actor?.lab_id), [actor, labsState.data]);

  async function save(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!token) return;
    const values = Object.fromEntries(new FormData(event.currentTarget)); if (dialog === "edit") delete values.lab_id;
    setBusy(true); setFormError("");
    try { const response = await apiRequest<DataRow>(dialog === "edit" && selected ? `/storage-locations/${selected.storage_location_id}` : "/storage-locations", { method: dialog === "edit" ? "PATCH" : "POST", body: JSON.stringify(values) }, token); showToast(response.message ?? "Storage location saved."); setDialog(null); setSelected(null); await locationsState.refresh(); }
    catch (caught) { setFormError(caught instanceof ApiError ? caught.message : "Storage location could not be saved."); } finally { setBusy(false); }
  }

  if (labsState.loading || locationsState.loading) return <LoadingState label="Loading storage coordinates…" />;
  if (labsState.error || locationsState.error || !labsState.data || !locationsState.data) return <ErrorState message={labsState.error || locationsState.error || "Storage data is unavailable."} onRetry={() => { void labsState.refresh(); void locationsState.refresh(); }} />;
  return (
    <>
      <PageHeader eyebrow="Physical organization" title="Storage Locations" description="Maintain laboratory cabinet, shelf and drawer coordinates with application-level null-normalized duplicate protection." actions={<Button onClick={() => { setSelected(null); setDialog("create"); }}><Icon name="plus" size={17} />Create Location</Button>} />
      <Panel>
        <SectionHeader title="Location directory" description="Blank shelf/drawer coordinates are normalized by the service before duplicate checks." action={<label className="field min-w-60"><span className="sr-only">Laboratory</span><Select value={effectiveLabId} onChange={(event) => { setLabId(event.target.value); setSelected(null); }}>{permittedLabs.map((lab) => <option key={String(lab.lab_id)} value={String(lab.lab_id)}>{String(lab.lab_name)}</option>)}</Select></label>} />
        <DataTable rows={locationsState.data} columns={columns} idKey="storage_location_id" selectedId={selected?.storage_location_id} onRowClick={setSelected} emptyTitle="No storage locations" emptyDescription="Create a cabinet, shelf, drawer or bin for the selected laboratory." />
      </Panel>
      {selected ? <Panel><SectionHeader title={`Location ${selected.storage_location_id}`} description={`Cabinet ${selected.cabinet_no} · Shelf ${selected.shelf_no || "—"} · Drawer ${selected.drawer_no || "—"}`} action={<Button variant="secondary" onClick={() => setDialog("edit")}><Icon name="edit" size={16} />Edit Location</Button>} /></Panel> : null}
      <Dialog open={dialog !== null} onClose={() => setDialog(null)} title={dialog === "edit" ? "Update storage location" : "Create storage location"} description="The selected laboratory is checked server-side; blank coordinates remain nullable in MySQL.">
        <form className="form-grid" onSubmit={save}>
          {dialog === "create" ? <Field label="Laboratory" htmlFor="location_lab" required><Select id="location_lab" name="lab_id" defaultValue={effectiveLabId} required>{permittedLabs.map((lab) => <option key={String(lab.lab_id)} value={String(lab.lab_id)}>{String(lab.lab_name)}</option>)}</Select></Field> : null}
          <Field label="Cabinet number" htmlFor="cabinet_no" required><Input id="cabinet_no" name="cabinet_no" defaultValue={dialog === "edit" ? String(selected?.cabinet_no ?? "") : ""} required /></Field>
          <Field label="Shelf number" htmlFor="shelf_no"><Input id="shelf_no" name="shelf_no" defaultValue={dialog === "edit" ? String(selected?.shelf_no ?? "") : ""} /></Field>
          <Field label="Drawer / bin number" htmlFor="drawer_no"><Input id="drawer_no" name="drawer_no" defaultValue={dialog === "edit" ? String(selected?.drawer_no ?? "") : ""} /></Field>
          <Field label="Location type" htmlFor="location_type" required><Select id="location_type" name="location_type" defaultValue={dialog === "edit" ? String(selected?.location_type ?? "CABINET") : "CABINET"}>{["CABINET", "SHELF", "DRAWER", "BIN"].map((type) => <option key={type}>{type}</option>)}</Select></Field>
          {formError ? <div className="inline-error full"><Icon name="alert" size={18} />{formError}</div> : null}<div className="form-actions"><Button type="button" variant="secondary" onClick={() => setDialog(null)}>Cancel</Button><Button type="submit" busy={busy}>{dialog === "edit" ? "Save Changes" : "Create Location"}</Button></div>
        </form>
      </Dialog>
    </>
  );
}
