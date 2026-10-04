"use client";

import Link from "next/link";
import { Icon } from "@/components/icon";
import { MetricCard, Panel } from "@/components/ui/card";
import { SectionHeader } from "@/components/ui/page";
import { ErrorState, LoadingState } from "@/components/ui/states";
import { formatValue, humanize } from "@/lib/format";
import { useAuth } from "@/lib/auth";
import { useApiData } from "@/lib/use-api-data";
import type { DashboardData, Role } from "@/types/api";

const kpiOrder = [
  "laboratory_count", "user_count", "component_count", "inventory_row_count",
  "total_available_stock", "total_reserved_stock", "inventory_valuation", "low_stock_count",
  "open_request_count", "active_transfer_count", "overdue_return_count", "disposed_quantity",
];

const kpiIcons: Record<string, string> = {
  laboratory_count: "lab", user_count: "users", component_count: "component",
  inventory_row_count: "storage", total_available_stock: "inventory",
  total_reserved_stock: "transfer", inventory_valuation: "reports", low_stock_count: "alert",
  open_request_count: "request", active_transfer_count: "transfer",
  overdue_return_count: "alert", disposed_quantity: "disposal",
};

const primaryByRole: Record<Role, string[]> = {
  STUDENT: ["component_count", "total_available_stock", "open_request_count", "low_stock_count"],
  FACULTY: ["total_available_stock", "open_request_count", "low_stock_count", "overdue_return_count"],
  LAB_ASSISTANT: ["total_available_stock", "total_reserved_stock", "low_stock_count", "active_transfer_count"],
  ADMINISTRATOR: ["inventory_valuation", "total_available_stock", "open_request_count", "active_transfer_count"],
};

const quickActions: Record<Role, Array<{ label: string; href: string; icon: string }>> = {
  STUDENT: [
    { label: "Browse components", href: "/components", icon: "component" },
    { label: "Create request", href: "/requests", icon: "request" },
  ],
  FACULTY: [
    { label: "Review requests", href: "/requests", icon: "request" },
    { label: "Monitor transfers", href: "/transfers", icon: "transfer" },
  ],
  LAB_ASSISTANT: [
    { label: "Open inventory", href: "/inventory", icon: "inventory" },
    { label: "Process transfers", href: "/transfers", icon: "transfer" },
  ],
  ADMINISTRATOR: [
    { label: "System oversight", href: "/reports", icon: "reports" },
    { label: "Manage laboratories", href: "/laboratories", icon: "lab" },
  ],
};

export function DashboardView() {
  const { actor } = useAuth();
  const { data, loading, error, refresh } = useApiData<DashboardData>("/dashboard");
  if (loading) return <LoadingState label="Preparing your operational dashboard…" />;
  if (error || !data || !actor) return <ErrorState message={error || "Dashboard data is unavailable."} onRetry={refresh} />;

  const stockMax = Math.max(1, ...data.stock_by_lab.flatMap((row) => [Number(row.quantity_available ?? 0), Number(row.quantity_reserved ?? 0)]));
  const requestTotal = Math.max(1, data.request_status.reduce((sum, row) => sum + Number(row.request_count ?? 0), 0));
  const primary = primaryByRole[actor.role].filter((key) => key in data.kpis);
  const secondary = kpiOrder.filter((key) => key in data.kpis && !primary.includes(key));
  const firstName = actor.full_name.split(" ")[0];

  return (
    <>
      <section className="dashboard-hero">
        <div>
          <p className="eyebrow light">Operational command centre</p>
          <h1>Welcome, {firstName}</h1>
          <p>Your dashboard is limited to the responsibilities and information approved for the {humanize(actor.role)} role.</p>
          <div className="dashboard-context">
            <span><Icon name="shield" size={16} />{humanize(actor.role)}</span>
            <span><Icon name="lab" size={16} />Laboratory {actor.lab_id}</span>
          </div>
        </div>
        <nav className="quick-actions" aria-label="Role-specific quick actions">
          {quickActions[actor.role].map((action) => (
            <Link href={action.href} key={action.href}>
              <Icon name={action.icon} size={18} />
              <span>{action.label}</span>
              <Icon name="arrow" size={16} />
            </Link>
          ))}
        </nav>
      </section>
      <SectionHeader title="Key indicators" description="The four measures most relevant to your current role and laboratory scope." />
      <section className="metric-grid" aria-label="Key performance indicators">
        {primary.map((key) => (
          <MetricCard key={key} label={humanize(key.replace("total_", ""))} value={formatValue(key, data.kpis[key])} icon={kpiIcons[key]} support={key === "inventory_valuation" ? "Available + reserved stock on hand" : "Current authorized scope"} />
        ))}
      </section>
      {secondary.length ? (
        <Panel className="pulse-panel">
          <SectionHeader title="Operational pulse" description="Supporting measures at a compact, decision-friendly density." action={<Icon name="pulse" size={20} />} />
          <dl className="pulse-grid">
            {secondary.map((key) => (
              <div key={key}>
                <dt>{humanize(key.replace("total_", ""))}</dt>
                <dd>{formatValue(key, data.kpis[key])}</dd>
              </div>
            ))}
          </dl>
        </Panel>
      ) : null}
      <div className="panel-grid">
        <Panel>
          <SectionHeader title="Stock by laboratory" description="Available stock compared with approved-but-undispatched reservations." action={<div className="legend"><span><i />Available</span><span><i />Reserved</span></div>} />
          {data.stock_by_lab.length ? (
            <div className="chart" role="img" aria-label="Available and reserved stock by laboratory">
              {data.stock_by_lab.map((row) => (
                <div className="chart-column" key={String(row.lab_id ?? row.lab_name)}>
                  <div className="chart-bars">
                    <div className="chart-bar" title={`Available ${row.quantity_available}`} style={{ height: `${Math.max(2, Number(row.quantity_available ?? 0) / stockMax * 100)}%` }} />
                    <div className="chart-bar secondary" title={`Reserved ${row.quantity_reserved}`} style={{ height: `${Math.max(2, Number(row.quantity_reserved ?? 0) / stockMax * 100)}%` }} />
                  </div>
                  <span title={String(row.lab_name)}>{String(row.lab_name)}</span>
                </div>
              ))}
            </div>
          ) : <p className="text-sm text-slate-500">No inventory is available in this scope.</p>}
        </Panel>
        <Panel>
          <SectionHeader title="Request status distribution" description="Current request workload at the correct request-header grain." />
          <div className="distribution">
            {data.request_status.length ? data.request_status.map((row) => {
              const count = Number(row.request_count ?? 0);
              return (
                <div className="distribution-row" key={String(row.request_status)}>
                  <span>{humanize(String(row.request_status))}</span>
                  <div className="distribution-track"><div className="distribution-fill" style={{ width: `${count / requestTotal * 100}%` }} /></div>
                  <strong>{count}</strong>
                </div>
              );
            }) : <p className="text-sm text-slate-500">No requests are visible in this scope.</p>}
          </div>
        </Panel>
      </div>
    </>
  );
}
