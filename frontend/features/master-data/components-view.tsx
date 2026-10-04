"use client";

import { useMemo, useState } from "react";
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
import { useApiData } from "@/lib/use-api-data";
import type { DataRow } from "@/types/api";

const columns = [
  { key: "component_id", label: "ID", numeric: true }, { key: "component_name", label: "Component" },
  { key: "part_number", label: "Part Number" }, { key: "category_id", label: "Category ID", numeric: true },
  { key: "unit_of_measure", label: "Unit" }, { key: "minimum_stock_level", label: "Minimum", numeric: true },
  { key: "manufacturer_details", label: "Manufacturer" },
];

export function ComponentsView() {
  const { actor, token } = useAuth(); const { showToast } = useToast();
  const categoryState = useApiData<DataRow[]>("/categories");
  const componentState = useApiData<DataRow[]>("/components");
  const [categoryFilter, setCategoryFilter] = useState("ALL");
  const [selected, setSelected] = useState<DataRow | null>(null);
  const [dialog, setDialog] = useState<"category" | "create" | "edit" | null>(null);
  const [busy, setBusy] = useState(false); const [formError, setFormError] = useState("");
  const filtered = useMemo(() => categoryFilter === "ALL" ? componentState.data ?? [] : (componentState.data ?? []).filter((row) => String(row.category_id) === categoryFilter), [categoryFilter, componentState.data]);

  async function saveCategory(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!token) return;
    const values = Object.fromEntries(new FormData(event.currentTarget)); setBusy(true); setFormError("");
    try { const response = await apiRequest<DataRow>("/categories", { method: "POST", body: JSON.stringify(values) }, token); showToast(response.message ?? "Category created."); setDialog(null); await categoryState.refresh(); }
    catch (caught) { setFormError(caught instanceof ApiError ? caught.message : "Category could not be created."); } finally { setBusy(false); }
  }
  async function saveComponent(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!token) return;
    const values = Object.fromEntries(new FormData(event.currentTarget)); setBusy(true); setFormError("");
    try { const response = await apiRequest<DataRow>(dialog === "edit" && selected ? `/components/${selected.component_id}` : "/components", { method: dialog === "edit" ? "PATCH" : "POST", body: JSON.stringify(values) }, token); showToast(response.message ?? "Component saved."); setDialog(null); setSelected(null); await componentState.refresh(); }
    catch (caught) { setFormError(caught instanceof ApiError ? caught.message : "Component could not be saved."); } finally { setBusy(false); }
  }

  if (categoryState.loading || componentState.loading) return <LoadingState label="Loading the component catalogue…" />;
  if (categoryState.error || componentState.error || !categoryState.data || !componentState.data) return <ErrorState message={categoryState.error || componentState.error || "Catalogue data is unavailable."} onRetry={() => { void categoryState.refresh(); void componentState.refresh(); }} />;
  const admin = actor?.role === "ADMINISTRATOR";
  return (
    <>
      <PageHeader eyebrow="Normalized catalogue" title="Component Catalogue" description="Search electronic components, part numbers and technical specifications classified through COMPONENT_CATEGORY." actions={admin ? <><Button variant="secondary" onClick={() => setDialog("category")}><Icon name="plus" size={17} />New Category</Button><Button onClick={() => { setSelected(null); setDialog("create"); }}><Icon name="plus" size={17} />Add Component</Button></> : undefined} />
      <Panel>
        <SectionHeader title="Electronic component directory" description="Use the category selector and table search to locate required laboratory components." action={<label className="field min-w-52"><span className="sr-only">Filter category</span><Select value={categoryFilter} onChange={(event) => setCategoryFilter(event.target.value)}><option value="ALL">All categories</option>{categoryState.data.map((category) => <option key={String(category.category_id)} value={String(category.category_id)}>{String(category.category_name)}</option>)}</Select></label>} />
        <DataTable rows={filtered} columns={columns} idKey="component_id" selectedId={selected?.component_id} onRowClick={setSelected} searchPlaceholder="Search component, part number or manufacturer" emptyTitle="No components found" emptyDescription="No component matches this category or search." />
      </Panel>
      {selected ? <Panel><SectionHeader title={String(selected.component_name)} description={String(selected.part_number || "No part number recorded")} action={admin ? <Button variant="secondary" onClick={() => setDialog("edit")}><Icon name="edit" size={16} />Edit Component</Button> : undefined} /><div className="detail-grid"><div className="detail-item"><span>Specification</span><strong>{String(selected.specification || "—")}</strong></div><div className="detail-item"><span>Unit</span><strong>{String(selected.unit_of_measure)}</strong></div><div className="detail-item"><span>Minimum stock</span><strong>{String(selected.minimum_stock_level)}</strong></div></div></Panel> : null}
      <Dialog open={dialog === "category"} onClose={() => setDialog(null)} title="Create component category" description="Categories classify components without duplicating descriptions."><form className="form-grid" onSubmit={saveCategory}><Field label="Category name" htmlFor="category_name" required><Input id="category_name" name="category_name" required /></Field><Field label="Description" htmlFor="description"><TextArea id="description" name="description" /></Field>{formError ? <div className="inline-error full"><Icon name="alert" size={18} />{formError}</div> : null}<div className="form-actions"><Button type="button" variant="secondary" onClick={() => setDialog(null)}>Cancel</Button><Button type="submit" busy={busy}>Create Category</Button></div></form></Dialog>
      <Dialog open={dialog === "create" || dialog === "edit"} onClose={() => setDialog(null)} title={dialog === "edit" ? "Update component" : "Add component"} description="Maintain the frozen COMPONENT attributes and minimum-stock threshold." wide>
        <form className="form-grid" onSubmit={saveComponent}>
          <Field label="Category" htmlFor="category_id" required><Select id="category_id" name="category_id" defaultValue={dialog === "edit" ? String(selected?.category_id ?? "") : ""} required><option value="" disabled>Select category</option>{categoryState.data.map((category) => <option key={String(category.category_id)} value={String(category.category_id)}>{String(category.category_name)}</option>)}</Select></Field>
          <Field label="Component name" htmlFor="component_name" required><Input id="component_name" name="component_name" defaultValue={dialog === "edit" ? String(selected?.component_name ?? "") : ""} required /></Field>
          <Field label="Part number" htmlFor="part_number"><Input id="part_number" name="part_number" defaultValue={dialog === "edit" ? String(selected?.part_number ?? "") : ""} /></Field>
          <Field label="Unit of measure" htmlFor="unit_of_measure" required><Input id="unit_of_measure" name="unit_of_measure" defaultValue={dialog === "edit" ? String(selected?.unit_of_measure ?? "piece") : "piece"} required /></Field>
          <Field label="Minimum stock level" htmlFor="minimum_stock_level" required><Input id="minimum_stock_level" name="minimum_stock_level" type="number" min="0" defaultValue={dialog === "edit" ? String(selected?.minimum_stock_level ?? 0) : "0"} required /></Field>
          <Field label="Manufacturer" htmlFor="manufacturer_details"><Input id="manufacturer_details" name="manufacturer_details" defaultValue={dialog === "edit" ? String(selected?.manufacturer_details ?? "") : ""} /></Field>
          <Field label="Specification" htmlFor="specification"><TextArea id="specification" name="specification" defaultValue={dialog === "edit" ? String(selected?.specification ?? "") : ""} /></Field>
          {formError ? <div className="inline-error full"><Icon name="alert" size={18} />{formError}</div> : null}<div className="form-actions"><Button type="button" variant="secondary" onClick={() => setDialog(null)}>Cancel</Button><Button type="submit" busy={busy}>{dialog === "edit" ? "Save Changes" : "Add Component"}</Button></div>
        </form>
      </Dialog>
    </>
  );
}
