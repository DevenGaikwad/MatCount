"use client";

import { useMemo, useState } from "react";
import { Icon } from "@/components/icon";
import { useToast } from "@/components/toast";
import { Button } from "@/components/ui/button";
import { MetricCard, Panel } from "@/components/ui/card";
import { DataTable } from "@/components/ui/data-table";
import { Dialog } from "@/components/ui/dialog";
import { Field, Input, Select, TextArea } from "@/components/ui/fields";
import { PageHeader, SectionHeader } from "@/components/ui/page";
import { ErrorState, LoadingState } from "@/components/ui/states";
import { ApiError, apiRequest } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { today } from "@/lib/format";
import { useApiData } from "@/lib/use-api-data";
import type { DataRow } from "@/types/api";

const columns = [
  { key: "disposal_id", label: "Record", numeric: true },
  { key: "disposal_date", label: "Date" },
  { key: "component_name", label: "Component" },
  { key: "lab_name", label: "Laboratory" },
  { key: "quantity_disposed", label: "Quantity", numeric: true },
  { key: "disposed_value", label: "Estimated Value", numeric: true },
  { key: "disposal_method", label: "Method" },
  { key: "disposal_reason", label: "Reason" },
];

export function DisposalView() {
  const { token } = useAuth();
  const { showToast } = useToast();
  const history = useApiData<DataRow[]>("/disposals");
  const inventory = useApiData<DataRow[]>("/inventory?limit=2000");
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [formError, setFormError] = useState("");
  const [inventoryId, setInventoryId] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [confirmation, setConfirmation] = useState("");

  const inventoryById = useMemo(() => new Map((inventory.data ?? []).map((row) => [Number(row.inventory_id), row])), [inventory.data]);
  const rows = useMemo<DataRow[]>(() => (history.data ?? []).map((row): DataRow => {
    const position = inventoryById.get(Number(row.inventory_id));
    return {
      ...row,
      component_name: position?.component_name ?? `Inventory ${row.inventory_id}`,
      lab_name: position?.lab_name ?? `Lab ${position?.lab_id ?? "—"}`,
      disposed_value: Number(row.quantity_disposed ?? 0) * Number(position?.unit_cost ?? 0),
    };
  }), [history.data, inventoryById]);
  const selectable = (inventory.data ?? []).filter((row) => Number(row.quantity_available) > 0 && !["BLOCKED", "INACTIVE"].includes(String(row.inventory_status)));
  const selected = inventoryById.get(Number(inventoryId));
  const totalQuantity = rows.reduce((sum, row) => sum + Number(row["quantity_disposed"] ?? 0), 0);
  const totalValue = rows.reduce((sum, row) => sum + Number(row["disposed_value"] ?? 0), 0);
  const currentYear = String(new Date().getFullYear());
  const thisYear = rows.filter((row) => String(row["disposal_date"]).startsWith(currentYear)).length;

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || confirmation !== "DISPOSE") return;
    const values = Object.fromEntries(new FormData(event.currentTarget));
    setBusy(true); setFormError("");
    try {
      const response = await apiRequest<DataRow>("/disposals", { method: "POST", body: JSON.stringify({ ...values, inventory_id: Number(inventoryId), quantity_disposed: quantity }) }, token);
      showToast(response.message ?? "Disposal recorded.");
      setOpen(false); setInventoryId(""); setQuantity(1); setConfirmation("");
      await Promise.all([history.refresh(), inventory.refresh()]);
    } catch (caught) {
      setFormError(caught instanceof ApiError ? caught.message : "The disposal could not be recorded.");
    } finally { setBusy(false); }
  }

  if (history.loading || inventory.loading) return <LoadingState label="Loading disposal register…" />;
  const error = history.error || inventory.error;
  if (error || !history.data || !inventory.data) return <ErrorState message={error || "Disposal data is unavailable."} onRetry={() => { void history.refresh(); void inventory.refresh(); }} />;

  return <>
    <PageHeader eyebrow="Authorized stock retirement" title="Disposal Register" description="Record irreversible stock retirement as an auditable event while the service atomically decrements only free available quantity." actions={<Button variant="danger" onClick={() => { setFormError(""); setOpen(true); }}><Icon name="disposal" size={17} />Record Disposal</Button>} />
    <div className="metric-grid">
      <MetricCard label="Disposal events" value={String(rows.length)} support="Immutable history records" icon="reports" />
      <MetricCard label="Units disposed" value={String(totalQuantity)} support="Across all authorized events" icon="disposal" />
      <MetricCard label="Estimated retired value" value={new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(totalValue)} support="At recorded inventory unit cost" icon="inventory" />
      <MetricCard label="Events this year" value={String(thisYear)} support={`Calendar year ${currentYear}`} icon="check" />
    </div>
    <Panel>
      <SectionHeader title="Disposal history" description="Every row identifies the inventory position, authorization, quantity, method, reason and date." />
      <DataTable rows={rows} columns={columns} idKey="disposal_id" pageSize={12} searchPlaceholder="Search component, laboratory, method or reason" emptyTitle="No disposal records" emptyDescription="Authorized disposal events will appear here without modifying prior history." />
    </Panel>

    <Dialog open={open} onClose={() => setOpen(false)} title="Record authorized disposal" description="This action reduces available stock and creates a permanent disposal record. It cannot be edited through SEMS." wide>
      <form className="form-grid" onSubmit={submit}>
        <Field label="Inventory position" htmlFor="disposal_inventory" required help="Only active positions with free available stock are selectable."><Select id="disposal_inventory" value={inventoryId} onChange={(event) => { setInventoryId(event.target.value); setQuantity(1); }} required><option value="">Select inventory position</option>{selectable.map((row) => <option key={String(row.inventory_id)} value={String(row.inventory_id)}>{String(row.component_name)} · {String(row.lab_name)} · Position {String(row.inventory_id)} · Available {String(row.quantity_available)}</option>)}</Select></Field>
        <Field label="Quantity to dispose" htmlFor="quantity_disposed" required><Input id="quantity_disposed" type="number" min="1" max={Number(selected?.quantity_available ?? 1)} value={quantity} onChange={(event) => setQuantity(Number(event.target.value))} required /></Field>
        <Field label="Disposal date" htmlFor="disposal_date" required><Input id="disposal_date" name="disposal_date" type="date" defaultValue={today()} required /></Field>
        <Field label="Disposal method" htmlFor="disposal_method" required><Select id="disposal_method" name="disposal_method" defaultValue="AUTHORIZED E-WASTE HANDOVER" required><option>AUTHORIZED E-WASTE HANDOVER</option><option>RECYCLING</option><option>SAFE DESTRUCTION</option><option>RETURN TO AUTHORIZED AGENCY</option></Select></Field>
        <Field label="Disposal reason" htmlFor="disposal_reason" required><TextArea id="disposal_reason" name="disposal_reason" placeholder="State the verified condition and reason for retirement." required /></Field>
        <Field label="Remarks" htmlFor="remarks"><TextArea id="remarks" name="remarks" placeholder="Optional authorization or handling notes." /></Field>
        {selected ? <div className="danger-panel panel full"><SectionHeader title="Stock impact confirmation" description={`${String(selected.component_name)} at ${String(selected.lab_name)}`} /><div className="detail-grid"><div className="detail-item"><span>Current available</span><strong>{String(selected.quantity_available)}</strong></div><div className="detail-item"><span>After disposal</span><strong>{Math.max(0, Number(selected.quantity_available) - quantity)}</strong></div><div className="detail-item"><span>Estimated value</span><strong>{new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(quantity * Number(selected.unit_cost ?? 0))}</strong></div></div><Field label='Type "DISPOSE" to authorize' htmlFor="disposal_confirmation" required><Input id="disposal_confirmation" value={confirmation} onChange={(event) => setConfirmation(event.target.value.toUpperCase())} autoComplete="off" required /></Field></div> : null}
        {formError ? <div className="inline-error full"><Icon name="alert" size={18} />{formError}</div> : null}
        <div className="form-actions"><Button type="button" variant="secondary" onClick={() => setOpen(false)}>Cancel</Button><Button type="submit" variant="danger" busy={busy} disabled={!selected || confirmation !== "DISPOSE"}>Confirm Disposal</Button></div>
      </form>
    </Dialog>
  </>;
}
