"use client";

import { useEffect, useMemo, useState } from "react";
import { Icon } from "@/components/icon";
import { useToast } from "@/components/toast";
import { Button } from "@/components/ui/button";
import { Panel } from "@/components/ui/card";
import { DataTable } from "@/components/ui/data-table";
import { Dialog } from "@/components/ui/dialog";
import { Field, Input, Select, TextArea } from "@/components/ui/fields";
import { PageHeader, SectionHeader } from "@/components/ui/page";
import { ErrorState, LoadingState } from "@/components/ui/states";
import { ApiError, apiRequest } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { today } from "@/lib/format";
import { useApiData } from "@/lib/use-api-data";
import type { DataRow, DetailPayload } from "@/types/api";

const columns = [
  { key: "request_id", label: "Request", numeric: true }, { key: "requesting_lab_id", label: "Lab", numeric: true },
  { key: "request_date", label: "Requested" }, { key: "required_by_date", label: "Required By" },
  { key: "priority", label: "Priority" }, { key: "request_status", label: "Status" }, { key: "reason", label: "Reason" },
];
type RequestAction = "create" | "review" | null;
interface DraftLine { key: number; component_id: string; quantity_requested: number; }

function plusDays(days: number) { const value = new Date(); value.setDate(value.getDate() + days); return value.toISOString().slice(0, 10); }

export function RequestsView() {
  const { actor, token } = useAuth(); const { showToast } = useToast();
  const requestState = useApiData<DataRow[]>("/requests"); const labsState = useApiData<DataRow[]>("/labs"); const componentsState = useApiData<DataRow[]>("/components");
  const [selected, setSelected] = useState<DataRow | null>(null); const [detail, setDetail] = useState<DetailPayload | null>(null);
  const [action, setAction] = useState<RequestAction>(null); const [busy, setBusy] = useState(false); const [formError, setFormError] = useState("");
  const [lines, setLines] = useState<DraftLine[]>([{ key: 1, component_id: "", quantity_requested: 1 }]);
  const [reviews, setReviews] = useState<Record<string, { quantity_approved: number; remarks: string }>>({});
  const [statusFilter, setStatusFilter] = useState("ALL");

  useEffect(() => {
    if (!selected || !token) return;
    apiRequest<DetailPayload>(`/requests/${selected.request_id}`, {}, token).then(({ data }) => setDetail(data)).catch(() => setDetail(null));
  }, [selected, token]);
  const visible = useMemo(() => statusFilter === "ALL" ? requestState.data ?? [] : (requestState.data ?? []).filter((row) => String(row.request_status) === statusFilter), [requestState.data, statusFilter]);
  const componentNames = useMemo(() => new Map((componentsState.data ?? []).map((item) => [String(item.component_id), String(item.component_name)])), [componentsState.data]);
  const detailRows: DataRow[] = (detail?.items ?? []).map((item): DataRow => ({ ...item, component_name: componentNames.get(String(item.component_id)) ?? `Component ${item.component_id}` }));
  const mayCreate = actor && ["STUDENT", "FACULTY", "ADMINISTRATOR"].includes(actor.role);
  const owns = selected && (Number(selected.created_by) === actor?.user_id || actor?.role === "ADMINISTRATOR");
  const canSubmit = selected?.request_status === "DRAFT" && owns;
  const canCancel = ["DRAFT", "SUBMITTED"].includes(String(selected?.request_status)) && owns;
  const canReview = actor && ["FACULTY", "ADMINISTRATOR"].includes(actor.role) && ["SUBMITTED", "PARTIALLY_APPROVED"].includes(String(selected?.request_status));

  async function mutate(path: string, message: string) {
    if (!token) return;
    try { const response = await apiRequest<DataRow>(path, { method: "POST" }, token); showToast(response.message ?? message); setSelected(null); setDetail(null); await requestState.refresh(); }
    catch (caught) { showToast(caught instanceof ApiError ? caught.message : "Request action failed.", "error"); }
  }
  async function createRequest(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!token) return;
    const values = Object.fromEntries(new FormData(event.currentTarget));
    const payload = { ...values, requesting_lab_id: actor?.role === "ADMINISTRATOR" ? values.requesting_lab_id : actor?.lab_id, items: lines.map((line) => ({ component_id: Number(line.component_id), quantity_requested: line.quantity_requested })) };
    setBusy(true); setFormError("");
    try { const response = await apiRequest<DataRow>("/requests", { method: "POST", body: JSON.stringify(payload) }, token); showToast(response.message ?? "Draft request created."); setAction(null); setLines([{ key: Date.now(), component_id: "", quantity_requested: 1 }]); await requestState.refresh(); }
    catch (caught) { setFormError(caught instanceof ApiError ? caught.message : "Request could not be created."); } finally { setBusy(false); }
  }
  function openReview() {
    const initial = Object.fromEntries((detail?.items ?? []).map((item) => [String(item.request_item_id), { quantity_approved: Number(item.quantity_approved ?? 0), remarks: String(item.remarks ?? "") }]));
    setReviews(initial); setFormError(""); setAction("review");
  }
  async function reviewRequest(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!token || !selected) return;
    setBusy(true); setFormError("");
    try { const response = await apiRequest<DataRow>(`/requests/${selected.request_id}/review`, { method: "POST", body: JSON.stringify({ reviews: Object.entries(reviews).map(([request_item_id, value]) => ({ request_item_id: Number(request_item_id), ...value })) }) }, token); showToast(response.message ?? "Request reviewed."); setAction(null); setSelected(null); setDetail(null); await requestState.refresh(); }
    catch (caught) { setFormError(caught instanceof ApiError ? caught.message : "Review could not be committed."); } finally { setBusy(false); }
  }

  if (requestState.loading || labsState.loading || componentsState.loading) return <LoadingState label="Loading component requests…" />;
  const combinedError = requestState.error || labsState.error || componentsState.error;
  if (combinedError || !requestState.data || !labsState.data || !componentsState.data) return <ErrorState message={combinedError || "Request data is unavailable."} onRetry={() => { void requestState.refresh(); void labsState.refresh(); void componentsState.refresh(); }} />;
  return (
    <>
      <PageHeader eyebrow="Approval workflow" title="Component Requests" description="Create, submit and review normalized multi-line requests with quantities and statuses controlled at both header and line level." actions={mayCreate ? <Button onClick={() => { setFormError(""); setAction("create"); }}><Icon name="plus" size={17} />Create Request</Button> : undefined} />
      <div className="split-workspace">
        <Panel>
          <SectionHeader title="Request register" description="Select a request to inspect its line-item progress and permitted next actions." action={<label className="field min-w-52"><span className="sr-only">Request status</span><Select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}><option value="ALL">All statuses</option>{["DRAFT", "SUBMITTED", "PARTIALLY_APPROVED", "APPROVED", "FULFILLED", "REJECTED", "CANCELLED"].map((status) => <option key={status}>{status.replaceAll("_", " ")}</option>)}</Select></label>} />
          <DataTable rows={visible} columns={columns} idKey="request_id" selectedId={selected?.request_id} onRowClick={(row) => { setDetail(null); setSelected(row); }} searchPlaceholder="Search request ID, reason, priority or status" emptyTitle="No requests found" emptyDescription="No component request matches this scope or status filter." />
        </Panel>
        <Panel className="sticky-detail">
          <SectionHeader title={selected ? `Request ${selected.request_id}` : "Request details"} description={selected ? String(selected.reason) : "Select a request from the register."} />
          {selected ? <>
            <div className="detail-grid"><div className="detail-item"><span>Status</span><strong>{String(selected.request_status).replaceAll("_", " ")}</strong></div><div className="detail-item"><span>Priority</span><strong>{String(selected.priority)}</strong></div><div className="detail-item"><span>Required by</span><strong>{String(selected.required_by_date)}</strong></div></div>
            <DataTable rows={detailRows} columns={[{ key: "request_item_id", label: "Line", numeric: true }, { key: "component_name", label: "Component" }, { key: "quantity_requested", label: "Requested", numeric: true }, { key: "quantity_approved", label: "Approved", numeric: true }, { key: "item_status", label: "Line Status" }, { key: "remarks", label: "Remarks" }]} pageSize={8} idKey="request_item_id" emptyTitle="Loading request items" emptyDescription="Line items will appear after the request detail loads." />
            <div className="page-actions mt-4">{canSubmit ? <Button onClick={() => void mutate(`/requests/${selected.request_id}/submit`, "Request submitted.")}>Submit Request</Button> : null}{canReview ? <Button onClick={openReview}>Review Request</Button> : null}{canCancel ? <Button variant="danger" onClick={() => window.confirm("Cancel this request before approval/allocation?") && void mutate(`/requests/${selected.request_id}/cancel`, "Request cancelled.")}>Cancel Request</Button> : null}</div>
          </> : <p className="text-sm text-slate-500">The header, line quantities and role-permitted workflow actions appear here.</p>}
        </Panel>
      </div>
      <Dialog open={action === "create"} onClose={() => setAction(null)} title="Create draft request" description="Add one unique line per component. The draft can be reviewed before submission." wide>
        <form className="form-grid" onSubmit={createRequest}>
          {actor?.role === "ADMINISTRATOR" ? <Field label="Requesting laboratory" htmlFor="requesting_lab_id" required><Select id="requesting_lab_id" name="requesting_lab_id" required>{labsState.data.map((lab) => <option key={String(lab.lab_id)} value={String(lab.lab_id)}>{String(lab.lab_name)}</option>)}</Select></Field> : <div className="detail-item"><span>Requesting laboratory</span><strong>Assigned Lab {actor?.lab_id}</strong></div>}
          <Field label="Request date" htmlFor="request_date" required><Input id="request_date" name="request_date" type="date" defaultValue={today()} required /></Field>
          <Field label="Required by" htmlFor="required_by_date" required><Input id="required_by_date" name="required_by_date" type="date" defaultValue={plusDays(7)} required /></Field>
          <Field label="Priority" htmlFor="priority" required><Select id="priority" name="priority" defaultValue="MEDIUM">{["LOW", "MEDIUM", "HIGH", "URGENT"].map((priority) => <option key={priority}>{priority}</option>)}</Select></Field>
          <Field label="Reason" htmlFor="reason" required><TextArea id="reason" name="reason" placeholder="Explain the laboratory requirement and intended use." required /></Field>
          <div className="full"><SectionHeader title="Request line items" description="Duplicate component lines are prohibited by the normalized schema." action={<Button type="button" variant="secondary" onClick={() => setLines((current) => [...current, { key: Date.now(), component_id: "", quantity_requested: 1 }])}><Icon name="plus" size={15} />Add Line</Button>} />
            <div className="grid gap-3">{lines.map((line, index) => <div className="grid grid-cols-[1fr_130px_40px] gap-3 items-end" key={line.key}><Field label={`Component ${index + 1}`} htmlFor={`component_${line.key}`} required><Select id={`component_${line.key}`} value={line.component_id} onChange={(event) => setLines((current) => current.map((item) => item.key === line.key ? { ...item, component_id: event.target.value } : item))} required><option value="">Select component</option>{componentsState.data!.map((component) => <option key={String(component.component_id)} value={String(component.component_id)} disabled={lines.some((other) => other.key !== line.key && other.component_id === String(component.component_id))}>{String(component.component_name)}{component.part_number ? ` · ${component.part_number}` : ""}</option>)}</Select></Field><Field label="Quantity" htmlFor={`quantity_${line.key}`} required><Input id={`quantity_${line.key}`} type="number" min="1" value={line.quantity_requested} onChange={(event) => setLines((current) => current.map((item) => item.key === line.key ? { ...item, quantity_requested: Number(event.target.value) } : item))} required /></Field><Button type="button" variant="ghost" aria-label={`Remove line ${index + 1}`} disabled={lines.length === 1} onClick={() => setLines((current) => current.filter((item) => item.key !== line.key))}><Icon name="close" size={17} /></Button></div>)}</div>
          </div>
          {formError ? <div className="inline-error full"><Icon name="alert" size={18} />{formError}</div> : null}<div className="form-actions"><Button type="button" variant="secondary" onClick={() => setAction(null)}>Cancel</Button><Button type="submit" busy={busy}>Create Draft Request</Button></div>
        </form>
      </Dialog>
      <Dialog open={action === "review"} onClose={() => setAction(null)} title={`Review request ${selected?.request_id ?? ""}`} description="Approved quantity must remain between zero and the requested quantity. All lines commit atomically." wide>
        <form className="grid gap-4" onSubmit={reviewRequest}>{detailRows.map((item) => { const key = String(item.request_item_id); const value = reviews[key] ?? { quantity_approved: 0, remarks: "" }; return <div className="panel" key={key}><SectionHeader title={String(item.component_name)} description={`Requested quantity: ${item.quantity_requested}`} /><div className="form-grid"><Field label="Approved quantity" htmlFor={`approved_${key}`} required><Input id={`approved_${key}`} type="number" min="0" max={Number(item.quantity_requested)} value={value.quantity_approved} onChange={(event) => setReviews((current) => ({ ...current, [key]: { ...value, quantity_approved: Number(event.target.value) } }))} required /></Field><Field label="Remarks" htmlFor={`remarks_${key}`}><Input id={`remarks_${key}`} value={value.remarks} onChange={(event) => setReviews((current) => ({ ...current, [key]: { ...value, remarks: event.target.value } }))} /></Field></div></div>; })}{formError ? <div className="inline-error"><Icon name="alert" size={18} />{formError}</div> : null}<div className="form-actions"><Button type="button" variant="secondary" onClick={() => setAction(null)}>Cancel</Button><Button type="submit" busy={busy}>Commit Review</Button></div></form>
      </Dialog>
    </>
  );
}
