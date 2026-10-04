"use client";

import { useEffect, useState } from "react";
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
import type { DataRow, Role } from "@/types/api";

const roles: Role[] = ["STUDENT", "FACULTY", "LAB_ASSISTANT", "ADMINISTRATOR"];
const statuses = ["ACTIVE", "INACTIVE", "SUSPENDED"];
const columns = [
  { key: "user_id", label: "User ID", numeric: true }, { key: "full_name", label: "Name" },
  { key: "email", label: "Email" }, { key: "role", label: "Role" },
  { key: "account_status", label: "Account Status" }, { key: "lab_id", label: "Lab", numeric: true },
];

export function UsersView() {
  const { token } = useAuth(); const { showToast } = useToast();
  const usersState = useApiData<DataRow[]>("/users");
  const labsState = useApiData<DataRow[]>("/labs");
  const [selected, setSelected] = useState<DataRow | null>(null);
  const [phones, setPhones] = useState<DataRow[]>([]);
  const [dialog, setDialog] = useState<"create" | "edit" | null>(null);
  const [busy, setBusy] = useState(false); const [formError, setFormError] = useState("");

  useEffect(() => {
    if (!selected || !token) return;
    apiRequest<DataRow[]>(`/users/${selected.user_id}/phones`, {}, token).then(({ data }) => setPhones(data)).catch(() => setPhones([]));
  }, [selected, token]);

  async function save(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!token) return;
    const values = Object.fromEntries(new FormData(event.currentTarget));
    setBusy(true); setFormError("");
    try {
      const response = await apiRequest<DataRow>(dialog === "edit" && selected ? `/users/${selected.user_id}` : "/users", { method: dialog === "edit" ? "PATCH" : "POST", body: JSON.stringify(values) }, token);
      showToast(response.message ?? "User saved."); setDialog(null); setSelected(null); await usersState.refresh();
    } catch (caught) { setFormError(caught instanceof ApiError ? caught.message : "User could not be saved."); }
    finally { setBusy(false); }
  }

  async function addPhone(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!token || !selected) return;
    const phone_number = String(new FormData(event.currentTarget).get("phone_number") ?? "");
    try {
      const response = await apiRequest<DataRow>(`/users/${selected.user_id}/phones`, { method: "POST", body: JSON.stringify({ phone_number }) }, token);
      showToast(response.message ?? "Phone added.");
      const refreshed = await apiRequest<DataRow[]>(`/users/${selected.user_id}/phones`, {}, token); setPhones(refreshed.data); event.currentTarget.reset();
    } catch (caught) { showToast(caught instanceof ApiError ? caught.message : "Phone could not be added.", "error"); }
  }

  if (usersState.loading || labsState.loading) return <LoadingState label="Loading users and role assignments…" />;
  if (usersState.error || labsState.error || !usersState.data || !labsState.data) return <ErrorState message={usersState.error || labsState.error || "User data is unavailable."} onRetry={() => { void usersState.refresh(); void labsState.refresh(); }} />;
  const labs = labsState.data;
  return (
    <>
      <PageHeader eyebrow="Administration" title="Users and Roles" description="Manage frozen USER records, laboratory assignments and account status. Authentication hashes remain outside the database." actions={<Button onClick={() => { setSelected(null); setDialog("create"); }}><Icon name="plus" size={17} />Create User</Button>} />
      <div className="split-workspace">
        <Panel><SectionHeader title="Authorized users" description="Select a user to view phone numbers or update role, laboratory and status." /><DataTable rows={usersState.data} columns={columns} idKey="user_id" selectedId={selected?.user_id} onRowClick={(row) => { setPhones([]); setSelected(row); }} emptyTitle="No users found" emptyDescription="Create an authorized user after laboratories are available." /></Panel>
        <Panel className="sticky-detail">
          <SectionHeader title={selected ? String(selected.full_name) : "User details"} description={selected ? String(selected.email) : "Select a user from the directory."} action={selected ? <Button variant="secondary" onClick={() => setDialog("edit")}><Icon name="edit" size={16} />Edit</Button> : undefined} />
          {selected ? <><div className="detail-grid"><div className="detail-item"><span>Role</span><strong>{String(selected.role).replaceAll("_", " ")}</strong></div><div className="detail-item"><span>Laboratory</span><strong>Lab {String(selected.lab_id)}</strong></div><div className="detail-item"><span>Status</span><strong>{String(selected.account_status)}</strong></div></div><DataTable rows={phones} columns={[{ key: "phone_number", label: "Phone Number" }]} pageSize={5} emptyTitle="No phone numbers" emptyDescription="Add a normalized USER_PHONE value below." /><form className="form-grid mt-4" onSubmit={addPhone}><Field label="New phone number" htmlFor="phone_number" required><Input id="phone_number" name="phone_number" placeholder="+91-90000-00001" required /></Field><div className="form-actions"><Button type="submit" variant="secondary">Add Phone</Button></div></form></> : <p className="text-sm text-slate-500">Identity details and phone numbers appear here after selection.</p>}
        </Panel>
      </div>
      <Dialog open={dialog !== null} onClose={() => setDialog(null)} title={dialog === "edit" ? "Update user" : "Create user"} description="Credentials are configured separately; this form maintains only the frozen USER attributes.">
        <form className="form-grid" onSubmit={save}>
          <Field label="Full name" htmlFor="full_name" required><Input id="full_name" name="full_name" defaultValue={dialog === "edit" ? String(selected?.full_name ?? "") : ""} required /></Field>
          <Field label="Email" htmlFor="email" required><Input id="email" name="email" type="email" defaultValue={dialog === "edit" ? String(selected?.email ?? "") : ""} required /></Field>
          <Field label="Assigned laboratory" htmlFor="lab_id" required><Select id="lab_id" name="lab_id" defaultValue={dialog === "edit" ? String(selected?.lab_id ?? "") : ""} required><option value="" disabled>Select a laboratory</option>{labs.map((lab) => <option key={String(lab.lab_id)} value={String(lab.lab_id)}>{String(lab.lab_name)}</option>)}</Select></Field>
          <Field label="Role" htmlFor="role" required><Select id="role" name="role" defaultValue={dialog === "edit" ? String(selected?.role ?? "STUDENT") : "STUDENT"}>{roles.map((role) => <option key={role} value={role}>{role.replaceAll("_", " ")}</option>)}</Select></Field>
          <Field label="Account status" htmlFor="account_status" required><Select id="account_status" name="account_status" defaultValue={dialog === "edit" ? String(selected?.account_status ?? "ACTIVE") : "ACTIVE"}>{statuses.map((status) => <option key={status}>{status}</option>)}</Select></Field>
          {formError ? <div className="inline-error full"><Icon name="alert" size={18} />{formError}</div> : null}
          <div className="form-actions"><Button type="button" variant="secondary" onClick={() => setDialog(null)}>Cancel</Button><Button type="submit" busy={busy}>{dialog === "edit" ? "Save Changes" : "Create User"}</Button></div>
        </form>
      </Dialog>
    </>
  );
}
