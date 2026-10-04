"use client";

import { useEffect, useState } from "react";
import { Icon } from "@/components/icon";
import { useToast } from "@/components/toast";
import { Button } from "@/components/ui/button";
import { Panel } from "@/components/ui/card";
import { DataTable } from "@/components/ui/data-table";
import { Dialog } from "@/components/ui/dialog";
import { Field, Input } from "@/components/ui/fields";
import { PageHeader, SectionHeader } from "@/components/ui/page";
import { ErrorState, LoadingState } from "@/components/ui/states";
import { ApiError, apiRequest } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useApiData } from "@/lib/use-api-data";
import type { DataRow } from "@/types/api";

const columns = [
  { key: "lab_id", label: "Lab ID", numeric: true },
  { key: "lab_name", label: "Laboratory" },
  { key: "department_name", label: "Department" },
  { key: "building_name", label: "Building" },
  { key: "lab_type", label: "Type" },
];

export function LaboratoriesView() {
  const { token } = useAuth();
  const { showToast } = useToast();
  const { data: labs, loading, error, refresh } = useApiData<DataRow[]>("/labs");
  const [selected, setSelected] = useState<DataRow | null>(null);
  const [contacts, setContacts] = useState<DataRow[]>([]);
  const [dialog, setDialog] = useState<"create" | "edit" | null>(null);
  const [busy, setBusy] = useState(false);
  const [formError, setFormError] = useState("");

  useEffect(() => {
    if (!selected || !token) return;
    apiRequest<DataRow[]>(`/labs/${selected.lab_id}/contacts`, {}, token)
      .then(({ data }) => setContacts(data)).catch(() => setContacts([]));
  }, [selected, token]);

  async function saveLab(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) return;
    const values = Object.fromEntries(new FormData(event.currentTarget));
    setBusy(true); setFormError("");
    try {
      const path = dialog === "edit" && selected ? `/labs/${selected.lab_id}` : "/labs";
      const response = await apiRequest<DataRow>(path, { method: dialog === "edit" ? "PATCH" : "POST", body: JSON.stringify(values) }, token);
      showToast(response.message ?? "Laboratory saved.");
      setDialog(null); setSelected(null); await refresh();
    } catch (caught) { setFormError(caught instanceof ApiError ? caught.message : "Laboratory could not be saved."); }
    finally { setBusy(false); }
  }

  async function addContact(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !selected) return;
    const number = String(new FormData(event.currentTarget).get("contact_number") ?? "");
    try {
      const response = await apiRequest<DataRow>(`/labs/${selected.lab_id}/contacts`, { method: "POST", body: JSON.stringify({ contact_number: number }) }, token);
      showToast(response.message ?? "Contact added.");
      const refreshed = await apiRequest<DataRow[]>(`/labs/${selected.lab_id}/contacts`, {}, token);
      setContacts(refreshed.data); event.currentTarget.reset();
    } catch (caught) { showToast(caught instanceof ApiError ? caught.message : "Contact could not be added.", "error"); }
  }

  if (loading) return <LoadingState label="Loading laboratory master data…" />;
  if (error || !labs) return <ErrorState message={error || "Laboratories are unavailable."} onRetry={refresh} />;
  return (
    <>
      <PageHeader eyebrow="Master data" title="Laboratories" description="Maintain the authoritative laboratory directory and normalized contact numbers without introducing an activation flag." actions={<Button onClick={() => { setSelected(null); setDialog("create"); }}><Icon name="plus" size={17} />Create Laboratory</Button>} />
      <div className="split-workspace">
        <Panel>
          <SectionHeader title="Laboratory directory" description="Select a row to inspect contacts or edit the laboratory." />
          <DataTable rows={labs} columns={columns} idKey="lab_id" selectedId={selected?.lab_id} onRowClick={(row) => { setContacts([]); setSelected(row); }} emptyTitle="No laboratories found" emptyDescription="Create the first laboratory to establish the SEMS operational structure." />
        </Panel>
        <Panel className="sticky-detail">
          <SectionHeader title={selected ? String(selected.lab_name) : "Laboratory details"} description={selected ? `Lab ${selected.lab_id} · ${selected.department_name}` : "Select a laboratory from the directory."} action={selected ? <Button variant="secondary" onClick={() => setDialog("edit")}><Icon name="edit" size={16} />Edit</Button> : undefined} />
          {selected ? (
            <>
              <div className="detail-grid"><div className="detail-item"><span>Building</span><strong>{String(selected.building_name)}</strong></div><div className="detail-item"><span>Type</span><strong>{String(selected.lab_type)}</strong></div><div className="detail-item"><span>Contacts</span><strong>{contacts.length}</strong></div></div>
              <DataTable rows={contacts} columns={[{ key: "contact_number", label: "Contact Number" }]} pageSize={5} emptyTitle="No contacts recorded" emptyDescription="Add a departmental contact number below." />
              <form className="form-grid mt-4" onSubmit={addContact}><Field label="New contact number" htmlFor="contact_number" required><Input id="contact_number" name="contact_number" placeholder="020-5550-1101" required /></Field><div className="form-actions"><Button type="submit" variant="secondary">Add Contact</Button></div></form>
            </>
          ) : <p className="text-sm text-slate-500">Laboratory contacts and maintenance actions appear here after selection.</p>}
        </Panel>
      </div>
      <Dialog open={dialog !== null} onClose={() => setDialog(null)} title={dialog === "edit" ? "Update laboratory" : "Create laboratory"} description="These values map directly to the frozen LAB relation.">
        <form className="form-grid" onSubmit={saveLab}>
          <Field label="Laboratory name" htmlFor="lab_name" required><Input id="lab_name" name="lab_name" defaultValue={dialog === "edit" ? String(selected?.lab_name ?? "") : ""} required /></Field>
          <Field label="Department" htmlFor="department_name" required><Input id="department_name" name="department_name" defaultValue={dialog === "edit" ? String(selected?.department_name ?? "") : ""} required /></Field>
          <Field label="Building" htmlFor="building_name" required><Input id="building_name" name="building_name" defaultValue={dialog === "edit" ? String(selected?.building_name ?? "") : ""} required /></Field>
          <Field label="Laboratory type" htmlFor="lab_type" required><Input id="lab_type" name="lab_type" defaultValue={dialog === "edit" ? String(selected?.lab_type ?? "") : ""} placeholder="Electronics" required /></Field>
          {formError ? <div className="inline-error full"><Icon name="alert" size={18} />{formError}</div> : null}
          <div className="form-actions"><Button type="button" variant="secondary" onClick={() => setDialog(null)}>Cancel</Button><Button type="submit" busy={busy}>{dialog === "edit" ? "Save Changes" : "Create Laboratory"}</Button></div>
        </form>
      </Dialog>
    </>
  );
}
