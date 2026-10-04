"use client";

import { useEffect, useMemo, useState } from "react";
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
import { today } from "@/lib/format";
import { useApiData } from "@/lib/use-api-data";
import type { DataRow, DetailPayload } from "@/types/api";

type Action = "plan" | "dispatch" | "receive" | "return" | null;
interface Allocation { key: number; inventory_id: string; quantity_sent: number; return_due_date: string; }
interface Receipt { transfer_item_id: number; quantity_received: number; mode: "inventory" | "location"; destination_id: string; }
interface ReturnLine { transfer_item_id: number; selected: boolean; destination_inventory_id: string; condition_on_return: string; }

const columns = [
  { key: "transfer_id", label: "Transfer", numeric: true },
  { key: "request_id", label: "Request", numeric: true },
  { key: "source_lab_name", label: "Source Lab" },
  { key: "destination_lab_name", label: "Destination Lab" },
  { key: "transfer_status", label: "Status" },
  { key: "approval_status", label: "Approval" },
  { key: "dispatch_date", label: "Dispatched" },
];

const flow = ["DRAFT", "APPROVED", "DISPATCHED", "RECEIVED", "RETURNED"];

function nextKey() { return Date.now() + Math.floor(Math.random() * 1000); }

export function TransfersView() {
  const { actor, token } = useAuth();
  const { showToast } = useToast();
  const mayOperate = actor?.role === "LAB_ASSISTANT" || actor?.role === "ADMINISTRATOR";
  const transfers = useApiData<DataRow[]>("/transfers");
  const labs = useApiData<DataRow[]>("/labs");
  const inventory = useApiData<DataRow[]>("/inventory?limit=2000");
  const locations = useApiData<DataRow[]>("/storage-locations", Boolean(mayOperate));
  const readyRequests = useApiData<DataRow[]>("/requests/transfer-ready", Boolean(mayOperate));
  const [selected, setSelected] = useState<DataRow | null>(null);
  const [detail, setDetail] = useState<DetailPayload | null>(null);
  const [requestDetail, setRequestDetail] = useState<DetailPayload | null>(null);
  const [action, setAction] = useState<Action>(null);
  const [busy, setBusy] = useState(false);
  const [formError, setFormError] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [sourceLab, setSourceLab] = useState("");
  const [requestId, setRequestId] = useState("");
  const [allocations, setAllocations] = useState<Allocation[]>([{ key: nextKey(), inventory_id: "", quantity_sent: 1, return_due_date: "" }]);
  const [conditions, setConditions] = useState<Record<string, string>>({});
  const [receipts, setReceipts] = useState<Receipt[]>([]);
  const [returns, setReturns] = useState<ReturnLine[]>([]);

  useEffect(() => {
    if (!selected || !token) return;
    apiRequest<DetailPayload>(`/transfers/${selected.transfer_id}`, {}, token)
      .then(({ data }) => setDetail(data))
      .catch(() => setDetail(null));
  }, [selected, token]);
  useEffect(() => {
    if (!requestId || !token) return;
    apiRequest<DetailPayload>(`/requests/${requestId}/transfer-plan`, {}, token)
      .then(({ data }) => setRequestDetail(data))
      .catch(() => setRequestDetail(null));
  }, [requestId, token]);

  const labNames = useMemo(() => new Map((labs.data ?? []).map((lab) => [Number(lab.lab_id), String(lab.lab_name)])), [labs.data]);
  const rows = useMemo<DataRow[]>(() => (transfers.data ?? []).map((row): DataRow => ({
    ...row,
    source_lab_name: labNames.get(Number(row.source_lab_id)) ?? `Lab ${row.source_lab_id}`,
    destination_lab_name: labNames.get(Number(row.destination_lab_id)) ?? `Lab ${row.destination_lab_id}`,
  })), [labNames, transfers.data]);
  const visible = statusFilter === "ALL" ? rows : rows.filter((row) => row.transfer_status === statusFilter);
  const sourceId = Number(sourceLab || actor?.lab_id || 0);
  const selectedRequest = (readyRequests.data ?? []).find((row) => String(row.request_id) === requestId);
  const destinationId = Number(selectedRequest?.requesting_lab_id ?? 0);
  const approvedComponents = new Set((requestDetail?.items ?? []).filter((item) => Number(item.quantity_approved) > 0).map((item) => Number(item.component_id)));
  const sourcePositions = (inventory.data ?? []).filter((row) => Number(row.lab_id) === sourceId && Number(row.quantity_available) > 0 && (!requestDetail || approvedComponents.has(Number(row.component_id))));
  const availableRequests = (readyRequests.data ?? []).filter((row) => Number(row.requesting_lab_id) !== sourceId);
  const destinationPositions = (inventory.data ?? []).filter((row) => Number(row.lab_id) === Number(selected?.destination_lab_id));
  const destinationLocations = (locations.data ?? []).filter((row) => Number(row.lab_id) === Number(selected?.destination_lab_id));
  const detailItems = detail?.items ?? [];
  const currentStatus = String(selected?.transfer_status ?? "");
  const sourceScoped = actor?.role === "ADMINISTRATOR" || Number(selected?.source_lab_id) === actor?.lab_id;
  const destinationScoped = actor?.role === "ADMINISTRATOR" || Number(selected?.destination_lab_id) === actor?.lab_id;

  function openAction(next: Exclude<Action, null>) {
    setFormError("");
    if (next === "dispatch") setConditions(Object.fromEntries(detailItems.map((item) => [String(item.transfer_item_id), String(item.condition_on_issue ?? "Good")] )));
    if (next === "receive") setReceipts(detailItems.map((item) => ({ transfer_item_id: Number(item.transfer_item_id), quantity_received: Number(item.quantity_received ?? 0), mode: "inventory", destination_id: "" })));
    if (next === "return") setReturns(detailItems.filter((item) => item.return_due_date && !item.return_date).map((item) => ({ transfer_item_id: Number(item.transfer_item_id), selected: false, destination_inventory_id: "", condition_on_return: "Good" })));
    setAction(next);
  }

  async function post(path: string, body?: unknown, message = "Transfer updated.") {
    if (!token) return false;
    setBusy(true); setFormError("");
    try {
      const response = await apiRequest<DataRow>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }, token);
      showToast(response.message ?? message); setAction(null); setSelected(null); setDetail(null); await transfers.refresh(); return true;
    } catch (caught) {
      setFormError(caught instanceof ApiError ? caught.message : "The transfer operation could not be completed."); return false;
    } finally { setBusy(false); }
  }

  async function planTransfer(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const valid = allocations.every((line) => line.inventory_id && line.quantity_sent > 0);
    if (!valid || !requestId || !destinationId) { setFormError("Select an approved request and complete every allocation."); return; }
    const completed = await post("/transfers", {
      request_id: Number(requestId), source_lab_id: sourceId, destination_lab_id: destinationId,
      allocations: allocations.map((line) => ({ inventory_id: Number(line.inventory_id), quantity_sent: line.quantity_sent, return_due_date: line.return_due_date || null })),
    }, "Draft transfer planned.");
    if (completed) { setRequestId(""); setRequestDetail(null); setAllocations([{ key: nextKey(), inventory_id: "", quantity_sent: 1, return_due_date: "" }]); }
  }

  async function submitDispatch(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!selected) return;
    const form = new FormData(event.currentTarget);
    await post(`/transfers/${selected.transfer_id}/dispatch`, { dispatch_date: form.get("dispatch_date"), items: detailItems.map((item) => ({ transfer_item_id: Number(item.transfer_item_id), condition_on_issue: conditions[String(item.transfer_item_id)] ?? "" })) });
  }
  async function submitReceipt(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!selected) return;
    const form = new FormData(event.currentTarget);
    await post(`/transfers/${selected.transfer_id}/receive`, { receipt_date: form.get("receipt_date"), items: receipts.map((line) => ({ transfer_item_id: line.transfer_item_id, quantity_received: line.quantity_received, destination_inventory_id: line.mode === "inventory" ? Number(line.destination_id) : null, storage_location_id: line.mode === "location" ? Number(line.destination_id) : null })) });
  }
  async function submitReturn(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!selected) return;
    const chosen = returns.filter((line) => line.selected);
    if (!chosen.length) { setFormError("Select at least one pending temporary item."); return; }
    const form = new FormData(event.currentTarget);
    await post(`/transfers/${selected.transfer_id}/return`, { return_date: form.get("return_date"), items: chosen.map((line) => ({ transfer_item_id: line.transfer_item_id, destination_inventory_id: Number(line.destination_inventory_id), condition_on_return: line.condition_on_return })) });
  }

  const errors = transfers.error || labs.error || inventory.error || (mayOperate ? locations.error || readyRequests.error : "");
  const loading = transfers.loading || labs.loading || inventory.loading || (mayOperate && (locations.loading || readyRequests.loading));
  if (loading) return <LoadingState label="Loading transfer workflow…" />;
  if (errors || !transfers.data || !labs.data || !inventory.data) return <ErrorState message={errors || "Transfer data is unavailable."} onRetry={() => { void transfers.refresh(); void labs.refresh(); void inventory.refresh(); if (mayOperate) { void locations.refresh(); void readyRequests.refresh(); } }} />;

  return <>
    <PageHeader eyebrow="Controlled stock movement" title="Inter-Laboratory Transfers" description="Plan approved-request allocations, reserve stock, dispatch, receive and return temporary assets through the frozen atomic workflow." actions={mayOperate ? <Button onClick={() => openAction("plan")}><Icon name="plus" size={17} />Plan Transfer</Button> : undefined} />
    <div className="split-workspace">
      <Panel>
        <SectionHeader title="Transfer register" description="Faculty have monitoring access; operational actions remain laboratory- and role-scoped." action={<label className="field min-w-52"><span className="sr-only">Transfer status</span><Select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}><option value="ALL">All statuses</option>{["DRAFT", "APPROVED", "DISPATCHED", "RECEIVED", "PARTIALLY_RETURNED", "RETURNED", "CANCELLED"].map((status) => <option key={status}>{status.replaceAll("_", " ")}</option>)}</Select></label>} />
        <DataTable rows={visible} columns={columns} idKey="transfer_id" selectedId={selected?.transfer_id} onRowClick={(row) => { setDetail(null); setSelected(row); }} searchPlaceholder="Search transfer, request, lab or status" emptyTitle="No transfers found" emptyDescription="No transfer matches this laboratory scope or status." />
      </Panel>
      <Panel className="sticky-detail">
        <SectionHeader title={selected ? `Transfer ${selected.transfer_id}` : "Transfer details"} description={selected ? `Request ${selected.request_id} · ${labNames.get(Number(selected.source_lab_id))} → ${labNames.get(Number(selected.destination_lab_id))}` : "Select a transfer to inspect its controlled lifecycle."} />
        {selected ? <>
          {currentStatus === "CANCELLED" ? <div className="inline-error"><Icon name="alert" size={18} />This transfer is closed and no longer operational.</div> : <div className="timeline">{flow.map((step, index) => { const position = currentStatus === "PARTIALLY_RETURNED" ? 3 : flow.indexOf(currentStatus); const className = index < position ? "complete" : index === position ? "current" : ""; return <div className={`timeline-step ${className}`} key={step}><span className="timeline-dot">{index < position ? "✓" : index + 1}</span><span>{step}</span></div>; })}</div>}
          <div className="detail-grid"><div className="detail-item"><span>Transfer status</span><strong>{currentStatus.replaceAll("_", " ")}</strong></div><div className="detail-item"><span>Approval</span><strong>{String(selected.approval_status)}</strong></div><div className="detail-item"><span>Dispatch date</span><strong>{String(selected.dispatch_date ?? "Not dispatched")}</strong></div></div>
          <DataTable rows={detailItems} columns={[{ key: "transfer_item_id", label: "Item", numeric: true }, { key: "component_name", label: "Component" }, { key: "quantity_sent", label: "Sent", numeric: true }, { key: "quantity_received", label: "Received", numeric: true }, { key: "return_due_date", label: "Return Due" }, { key: "return_date", label: "Returned" }]} pageSize={8} idKey="transfer_item_id" emptyTitle="Loading allocation lines" emptyDescription="Transfer lines appear after detail retrieval." />
          <div className="page-actions mt-4">
            {actor?.role === "ADMINISTRATOR" && currentStatus === "DRAFT" ? <><Button onClick={() => void post(`/transfers/${selected.transfer_id}/approve`)}>Approve & Reserve</Button><Button variant="danger" onClick={() => window.confirm("Reject this pending transfer?") && void post(`/transfers/${selected.transfer_id}/reject`)}>Reject</Button></> : null}
            {mayOperate && sourceScoped && currentStatus === "APPROVED" ? <Button onClick={() => openAction("dispatch")}>Record Dispatch</Button> : null}
            {mayOperate && destinationScoped && currentStatus === "DISPATCHED" ? <Button onClick={() => openAction("receive")}>Record Receipt</Button> : null}
            {mayOperate && ["RECEIVED", "PARTIALLY_RETURNED"].includes(currentStatus) && detailItems.some((item) => item.return_due_date && !item.return_date) ? <Button onClick={() => openAction("return")}>Record Return</Button> : null}
            {mayOperate && sourceScoped && ["DRAFT", "APPROVED"].includes(currentStatus) ? <Button variant="danger" onClick={() => window.confirm("Cancel this transfer? Approved reservations will be released atomically.") && void post(`/transfers/${selected.transfer_id}/cancel`)}>Cancel</Button> : null}
          </div>
          {formError && !action ? <div className="inline-error mt-3"><Icon name="alert" size={18} />{formError}</div> : null}
        </> : <p className="text-sm text-slate-500">Allocation, approval, movement dates, receipt progress and temporary-return evidence appear here.</p>}
      </Panel>
    </div>

    <Dialog open={action === "plan"} onClose={() => setAction(null)} title="Plan inter-laboratory transfer" description="Allocate available stock only against an approved request. Approval will reserve stock atomically." wide>
      <form className="form-grid" onSubmit={planTransfer}>
        {actor?.role === "ADMINISTRATOR" ? <Field label="Source laboratory" htmlFor="source_lab" required><Select id="source_lab" value={sourceLab} onChange={(event) => { setSourceLab(event.target.value); setRequestId(""); }} required><option value="">Select source laboratory</option>{labs.data.map((lab) => <option key={String(lab.lab_id)} value={String(lab.lab_id)}>{String(lab.lab_name)}</option>)}</Select></Field> : <div className="detail-item"><span>Source laboratory</span><strong>{labNames.get(actor?.lab_id ?? 0)}</strong></div>}
        <Field label="Approved destination request" htmlFor="request_id" required><Select id="request_id" value={requestId} onChange={(event) => { setRequestDetail(null); setRequestId(event.target.value); setAllocations([{ key: nextKey(), inventory_id: "", quantity_sent: 1, return_due_date: "" }]); }} required disabled={!sourceId}><option value="">Select approved request</option>{availableRequests.map((request) => <option key={String(request.request_id)} value={String(request.request_id)}>Request {String(request.request_id)} · {labNames.get(Number(request.requesting_lab_id))} · {String(request.priority)}</option>)}</Select></Field>
        <div className="detail-item full"><span>Destination laboratory</span><strong>{destinationId ? labNames.get(destinationId) : "Derived from the selected request"}</strong></div>
        <div className="full"><SectionHeader title="Stock allocations" description="Only positions matching an approved request line are shown after request detail loads." action={<Button type="button" variant="secondary" onClick={() => setAllocations((current) => [...current, { key: nextKey(), inventory_id: "", quantity_sent: 1, return_due_date: "" }])}><Icon name="plus" size={15} />Add Allocation</Button>} />
          <div className="grid gap-3">{allocations.map((line, index) => <div className="grid grid-cols-[1fr_110px_155px_40px] gap-3 items-end" key={line.key}><Field label={`Source position ${index + 1}`} htmlFor={`position_${line.key}`} required><Select id={`position_${line.key}`} value={line.inventory_id} onChange={(event) => setAllocations((current) => current.map((item) => item.key === line.key ? { ...item, inventory_id: event.target.value } : item))} required disabled={!requestDetail}><option value="">Select position</option>{sourcePositions.map((position) => <option key={String(position.inventory_id)} value={String(position.inventory_id)} disabled={allocations.some((other) => other.key !== line.key && other.inventory_id === String(position.inventory_id))}>{String(position.component_name)} · {String(position.lab_name)} · Available {String(position.quantity_available)}</option>)}</Select></Field><Field label="Quantity" htmlFor={`sent_${line.key}`} required><Input id={`sent_${line.key}`} type="number" min="1" value={line.quantity_sent} onChange={(event) => setAllocations((current) => current.map((item) => item.key === line.key ? { ...item, quantity_sent: Number(event.target.value) } : item))} required /></Field><Field label="Return due (optional)" htmlFor={`due_${line.key}`}><Input id={`due_${line.key}`} type="date" min={today()} value={line.return_due_date} onChange={(event) => setAllocations((current) => current.map((item) => item.key === line.key ? { ...item, return_due_date: event.target.value } : item))} /></Field><Button type="button" variant="ghost" aria-label={`Remove allocation ${index + 1}`} disabled={allocations.length === 1} onClick={() => setAllocations((current) => current.filter((item) => item.key !== line.key))}><Icon name="close" size={17} /></Button></div>)}</div>
        </div>
        {formError ? <div className="inline-error full"><Icon name="alert" size={18} />{formError}</div> : null}<div className="form-actions"><Button type="button" variant="secondary" onClick={() => setAction(null)}>Cancel</Button><Button type="submit" busy={busy}>Create Draft Transfer</Button></div>
      </form>
    </Dialog>

    <Dialog open={action === "dispatch"} onClose={() => setAction(null)} title={`Dispatch transfer ${selected?.transfer_id ?? ""}`} description="Record a condition for every allocation. Dispatch consumes reserved stock exactly once." wide>
      <form className="grid gap-4" onSubmit={submitDispatch}><Field label="Dispatch date" htmlFor="dispatch_date" required><Input id="dispatch_date" name="dispatch_date" type="date" defaultValue={today()} required /></Field>{detailItems.map((item) => <Field key={String(item.transfer_item_id)} label={`${String(item.component_name ?? `Inventory ${item.inventory_id}`)} · ${item.quantity_sent} units`} htmlFor={`condition_${item.transfer_item_id}`} required><Input id={`condition_${item.transfer_item_id}`} value={conditions[String(item.transfer_item_id)] ?? ""} onChange={(event) => setConditions((current) => ({ ...current, [String(item.transfer_item_id)]: event.target.value }))} placeholder="Condition on issue" required /></Field>)}{formError ? <div className="inline-error"><Icon name="alert" size={18} />{formError}</div> : null}<div className="form-actions"><Button type="button" variant="secondary" onClick={() => setAction(null)}>Cancel</Button><Button type="submit" busy={busy}>Confirm Dispatch</Button></div></form>
    </Dialog>

    <Dialog open={action === "receive"} onClose={() => setAction(null)} title={`Receive transfer ${selected?.transfer_id ?? ""}`} description="Enter cumulative received quantities and one matching destination for every allocation." wide>
      <form className="grid gap-4" onSubmit={submitReceipt}><Field label="Receipt date" htmlFor="receipt_date" required><Input id="receipt_date" name="receipt_date" type="date" min={String(selected?.dispatch_date ?? "")} defaultValue={today()} required /></Field>{receipts.map((line) => { const item = detailItems.find((candidate) => Number(candidate.transfer_item_id) === line.transfer_item_id); const candidates = destinationPositions.filter((position) => Number(position.component_id) === Number(item?.component_id)); return <div className="panel" key={line.transfer_item_id}><SectionHeader title={String(item?.component_name ?? `Transfer item ${line.transfer_item_id}`)} description={`Sent ${item?.quantity_sent} · previously received ${item?.quantity_received ?? 0}`} /><div className="form-grid"><Field label="Cumulative received" htmlFor={`received_${line.transfer_item_id}`} required><Input id={`received_${line.transfer_item_id}`} type="number" min={Number(item?.quantity_received ?? 0)} max={Number(item?.quantity_sent ?? 0)} value={line.quantity_received} onChange={(event) => setReceipts((current) => current.map((entry) => entry.transfer_item_id === line.transfer_item_id ? { ...entry, quantity_received: Number(event.target.value) } : entry))} required /></Field><Field label="Destination mode" htmlFor={`mode_${line.transfer_item_id}`} required><Select id={`mode_${line.transfer_item_id}`} value={line.mode} onChange={(event) => setReceipts((current) => current.map((entry) => entry.transfer_item_id === line.transfer_item_id ? { ...entry, mode: event.target.value as Receipt["mode"], destination_id: "" } : entry))}><option value="inventory">Existing inventory position</option><option value="location">New/matching storage location</option></Select></Field><Field label={line.mode === "inventory" ? "Destination position" : "Destination location"} htmlFor={`destination_${line.transfer_item_id}`} required><Select id={`destination_${line.transfer_item_id}`} value={line.destination_id} onChange={(event) => setReceipts((current) => current.map((entry) => entry.transfer_item_id === line.transfer_item_id ? { ...entry, destination_id: event.target.value } : entry))} required><option value="">Select destination</option>{(line.mode === "inventory" ? candidates : destinationLocations).map((candidate) => <option key={String(line.mode === "inventory" ? candidate.inventory_id : candidate.storage_location_id)} value={String(line.mode === "inventory" ? candidate.inventory_id : candidate.storage_location_id)}>{line.mode === "inventory" ? `${String(candidate.component_name)} · Position ${String(candidate.inventory_id)} · Available ${String(candidate.quantity_available)}` : `Cabinet ${String(candidate.cabinet_no)} · Shelf ${String(candidate.shelf_no ?? "—")} · Drawer ${String(candidate.drawer_no ?? "—")}`}</option>)}</Select></Field></div></div>; })}{formError ? <div className="inline-error"><Icon name="alert" size={18} />{formError}</div> : null}<div className="form-actions"><Button type="button" variant="secondary" onClick={() => setAction(null)}>Cancel</Button><Button type="submit" busy={busy}>Commit Receipt</Button></div></form>
    </Dialog>

    <Dialog open={action === "return"} onClose={() => setAction(null)} title={`Return temporary items · Transfer ${selected?.transfer_id ?? ""}`} description="Select pending temporary allocations and identify the current destination stock position." wide>
      <form className="grid gap-4" onSubmit={submitReturn}><Field label="Return date" htmlFor="return_date" required><Input id="return_date" name="return_date" type="date" min={String(selected?.received_date ?? "")} defaultValue={today()} required /></Field>{returns.map((line) => { const item = detailItems.find((candidate) => Number(candidate.transfer_item_id) === line.transfer_item_id); const candidates = destinationPositions.filter((position) => Number(position.component_id) === Number(item?.component_id) && Number(position.quantity_available) >= Number(item?.quantity_received)); return <div className="panel" key={line.transfer_item_id}><label className="flex items-start gap-3"><input type="checkbox" checked={line.selected} onChange={(event) => setReturns((current) => current.map((entry) => entry.transfer_item_id === line.transfer_item_id ? { ...entry, selected: event.target.checked } : entry))} /><span><strong>{String(item?.component_name ?? `Item ${line.transfer_item_id}`)}</strong><small className="block text-slate-500">Received {String(item?.quantity_received)} · due {String(item?.return_due_date)}</small></span></label>{line.selected ? <div className="form-grid mt-4"><Field label="Current destination position" htmlFor={`return_position_${line.transfer_item_id}`} required><Select id={`return_position_${line.transfer_item_id}`} value={line.destination_inventory_id} onChange={(event) => setReturns((current) => current.map((entry) => entry.transfer_item_id === line.transfer_item_id ? { ...entry, destination_inventory_id: event.target.value } : entry))} required><option value="">Select matching position</option>{candidates.map((position) => <option key={String(position.inventory_id)} value={String(position.inventory_id)}>Position {String(position.inventory_id)} · Available {String(position.quantity_available)}</option>)}</Select></Field><Field label="Condition on return" htmlFor={`return_condition_${line.transfer_item_id}`} required><Input id={`return_condition_${line.transfer_item_id}`} value={line.condition_on_return} onChange={(event) => setReturns((current) => current.map((entry) => entry.transfer_item_id === line.transfer_item_id ? { ...entry, condition_on_return: event.target.value } : entry))} required /></Field></div> : null}</div>; })}{formError ? <div className="inline-error"><Icon name="alert" size={18} />{formError}</div> : null}<div className="form-actions"><Button type="button" variant="secondary" onClick={() => setAction(null)}>Cancel</Button><Button type="submit" busy={busy}>Commit Selected Returns</Button></div></form>
    </Dialog>
  </>;
}
