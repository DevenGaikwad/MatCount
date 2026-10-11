"use client";

import { useEffect, useMemo, useState } from "react";
import { Icon } from "@/components/icon";
import { useToast } from "@/components/toast";
import { Button } from "@/components/ui/button";
import { AccessNotice } from "@/components/ui/access-notice";
import { MetricCard, Panel } from "@/components/ui/card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { PageHeader, SectionHeader } from "@/components/ui/page";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/states";
import { ApiError, apiRequest, downloadReport } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { formatValue, humanize } from "@/lib/format";
import { useApiData } from "@/lib/use-api-data";
import type { DataRow } from "@/types/api";

interface ReportOption extends DataRow { view_name: string; label: string; }

const metadata: Record<string, { description: string; grain: string }> = {
  v_inventory_detail: { description: "Position-level stock, storage coordinates and operational status.", grain: "One inventory position" },
  v_component_stock_summary: { description: "Available and reserved stock consolidated by component and laboratory.", grain: "One lab + component" },
  v_low_stock_components: { description: "Components at or below their minimum stock threshold.", grain: "One low-stock lab + component" },
  v_request_progress: { description: "Header-grain request progress without line-item double counting.", grain: "One component request" },
  v_transfer_detail: { description: "Traceable allocation, dispatch, receipt and temporary-return evidence.", grain: "One transfer item" },
  v_overdue_returns: { description: "Temporary transfer items past their return due date.", grain: "One overdue transfer item" },
  v_disposal_summary: { description: "Authorized disposal history with quantities and accountable lifecycle evidence.", grain: "One disposal event" },
};

const charts: Record<string, { label: string; first: string; second?: string; firstLabel: string; secondLabel?: string }> = {
  v_inventory_detail: { label: "component_name", first: "quantity_available", second: "quantity_reserved", firstLabel: "Available", secondLabel: "Reserved" },
  v_component_stock_summary: { label: "component_name", first: "quantity_available", second: "quantity_reserved", firstLabel: "Available", secondLabel: "Reserved" },
  v_low_stock_components: { label: "component_name", first: "quantity_available", second: "minimum_stock_level", firstLabel: "Available", secondLabel: "Minimum" },
  v_request_progress: { label: "request_id", first: "total_approved", second: "total_requested", firstLabel: "Approved", secondLabel: "Requested" },
  v_transfer_detail: { label: "component_name", first: "quantity_received", second: "quantity_sent", firstLabel: "Received", secondLabel: "Sent" },
  v_overdue_returns: { label: "component_name", first: "days_overdue", firstLabel: "Days overdue" },
  v_disposal_summary: { label: "component_name", first: "disposed_value", firstLabel: "Disposed value" },
};

export function ReportsView() {
  const { actor, token } = useAuth();
  const { showToast } = useToast();
  const catalogue = useApiData<ReportOption[]>("/reports");
  const [selected, setSelected] = useState("v_inventory_detail");
  const [rows, setRows] = useState<DataRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [downloading, setDownloading] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    if (!token || !selected || !catalogue.data?.some((item) => item.view_name === selected)) return;
    let active = true;
    const timer = window.setTimeout(() => {
      setLoading(true); setError("");
      apiRequest<DataRow[]>(`/reports/${selected}?limit=2000`, {}, token)
        .then(({ data }) => { if (active) setRows(data); })
        .catch((caught) => { if (active) setError(caught instanceof ApiError ? caught.message : "The selected report could not be loaded."); })
        .finally(() => { if (active) setLoading(false); });
    }, 0);
    return () => { active = false; window.clearTimeout(timer); };
  }, [catalogue.data, refreshKey, selected, token]);

  const columns = useMemo<Column[]>(() => {
    const first = rows[0];
    return first ? Object.keys(first).map((key) => ({ key, label: humanize(key), numeric: typeof first[key] === "number" })) : [];
  }, [rows]);
  // Identifiers are numeric fields, but summing them is not a useful report metric.
  const summaryMeasure: Record<string, string> = {
    v_inventory_detail: "quantity_available",
    v_component_stock_summary: "quantity_available",
    v_low_stock_components: "shortage_quantity",
    v_request_progress: "total_approved",
    v_transfer_detail: "quantity_received",
    v_overdue_returns: "quantity_received",
    v_disposal_summary: "quantity_disposed",
  };
  const summaryKey = summaryMeasure[selected];
  const hasSummary = Boolean(summaryKey) && rows.some((row) => summaryKey in row);
  const numericTotal = hasSummary ? rows.reduce((sum, row) => sum + Number(row[summaryKey] ?? 0), 0) : 0;
  const chart = selected === "v_disposal_summary" && !rows.some((row) => "disposed_value" in row)
    ? { label: "component_name", first: "quantity_disposed", firstLabel: "Disposed quantity" }
    : charts[selected];
  const chartRows = rows.slice(0, 12);
  const chartMax = Math.max(1, ...chartRows.flatMap((row) => [Number(row[chart.first] ?? 0), chart.second ? Number(row[chart.second] ?? 0) : 0]));
  const current = catalogue.data?.find((item) => item.view_name === selected);

  async function exportCsv() {
    if (!token) return;
    setDownloading(true);
    try { await downloadReport(selected, token); showToast("Formula-safe CSV report downloaded."); }
    catch (caught) { showToast(caught instanceof ApiError ? caught.message : "CSV export failed.", "error"); }
    finally { setDownloading(false); }
  }

  if (catalogue.loading) return <LoadingState label="Loading report catalogue…" />;
  if (catalogue.error || !catalogue.data) return <ErrorState message={catalogue.error || "Report catalogue is unavailable."} onRetry={catalogue.refresh} />;
  return <>
    <PageHeader eyebrow="Role-scoped analytics" title="Reports & Operational Intelligence" description="Read-only SQL-view reports preserve documented grains, laboratory scope and formula-safe export without bypassing the service layer." actions={<Button onClick={() => void exportCsv()} busy={downloading} disabled={!rows.length}><Icon name="download" size={17} />Export CSV</Button>} />
    <AccessNotice
      title={`${actor?.role === "ADMINISTRATOR" ? "Department-wide" : "Role-scoped"} reporting boundary`}
      description={actor?.role === "STUDENT" || actor?.role === "FACULTY" ? "Financial columns are removed by the server before tables and CSV exports are generated." : "Report rows are limited by your authenticated role and laboratory responsibilities."}
    />
    <div className="report-selector" role="list" aria-label="Available reports">
      {catalogue.data.map((report) => <button type="button" role="listitem" key={report.view_name} className={`report-option ${selected === report.view_name ? "active" : ""}`} onClick={() => setSelected(report.view_name)}><span className="report-option-icon"><Icon name={report.view_name.includes("transfer") || report.view_name.includes("overdue") ? "transfer" : report.view_name.includes("request") ? "request" : report.view_name.includes("disposal") ? "disposal" : "reports"} size={19} /></span><span><strong>{report.label}</strong><small>{metadata[report.view_name]?.grain}</small></span></button>)}
    </div>
    <div className="metric-grid report-metrics">
      <MetricCard label="Displayed records" value={String(rows.length)} support="Maximum 2,000 scoped rows" icon="reports" />
      <MetricCard label="Report grain" value={metadata[selected]?.grain ?? "Documented SQL view"} support="Aggregation-safe interpretation" icon="database" />
      <MetricCard label="Data fields" value={String(columns.length)} support="Returned by the authoritative view" icon="component" />
      <MetricCard label={hasSummary ? `Total ${humanize(summaryKey)}` : "Quantity summary"} value={hasSummary ? formatValue(summaryKey, numericTotal) : "Not applicable"} support="Total across returned scoped rows" icon="inventory" />
    </div>
    <div className="panel-grid">
      <Panel>
        <SectionHeader title={`${current?.label ?? humanize(selected)} overview`} description={metadata[selected]?.description} action={<div className="legend"><span><i />{chart.firstLabel}</span>{chart.second ? <span><i />{chart.secondLabel}</span> : null}</div>} />
        {loading ? <LoadingState label="Calculating scoped report…" /> : error ? <ErrorState message={error} onRetry={() => setRefreshKey((value) => value + 1)} /> : chartRows.length ? <div className="chart report-chart" role="img" aria-label={`${current?.label ?? selected} comparison chart`}>{chartRows.map((row, index) => <div className="chart-column" key={`${String(row[chart.label])}-${index}`}><div className="chart-bars"><div className="chart-bar" style={{ height: `${Math.max(2, Number(row[chart.first] ?? 0) / chartMax * 100)}%` }} title={`${chart.firstLabel}: ${formatValue(chart.first, row[chart.first])}`} />{chart.second ? <div className="chart-bar secondary" style={{ height: `${Math.max(2, Number(row[chart.second] ?? 0) / chartMax * 100)}%` }} title={`${chart.secondLabel}: ${formatValue(chart.second, row[chart.second])}`} /> : null}</div><span title={String(row[chart.label] ?? "")}>{selected === "v_request_progress" ? `Request ${String(row[chart.label])}` : String(row[chart.label] ?? "—")}</span></div>)}</div> : <EmptyState title="No chartable records" description="This report currently contains no rows in your authorized scope." />}
      </Panel>
      <Panel>
        <SectionHeader title="Interpretation notes" description="Use the declared grain before totals, comparisons or viva explanations." />
        <dl className="report-notes"><div><dt>Authoritative source</dt><dd>{selected}</dd></div><div><dt>Relational grain</dt><dd>{metadata[selected]?.grain}</dd></div><div><dt>Access scope</dt><dd>Applied by authenticated role and laboratory</dd></div><div><dt>Export safety</dt><dd>UTF-8 CSV with formula-like cells neutralized</dd></div><div><dt>Refresh model</dt><dd>Read directly from the shared MySQL reporting view</dd></div></dl>
      </Panel>
    </div>
    <Panel className="mt-5">
      <SectionHeader title={`${current?.label ?? humanize(selected)} data`} description={`All fields returned by ${selected}; search, sort and paginate without changing the underlying records.`} />
      {loading ? <LoadingState label="Loading report rows…" /> : error ? <ErrorState message={error} onRetry={() => setRefreshKey((value) => value + 1)} /> : <DataTable rows={rows} columns={columns} idKey={columns.find((column) => column.key.endsWith("_id"))?.key ?? columns[0]?.key} pageSize={15} searchPlaceholder="Search any value in this report" emptyTitle="No report rows" emptyDescription="No records are visible in the current authorized scope." />}
    </Panel>
  </>;
}
