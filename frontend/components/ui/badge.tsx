import { humanize } from "@/lib/format";

const positive = new Set(["ACTIVE", "AVAILABLE", "APPROVED", "FULFILLED", "RECEIVED", "RETURNED"]);
const warning = new Set(["LOW_STOCK", "SUBMITTED", "PARTIALLY_APPROVED", "DISPATCHED", "PARTIALLY_RETURNED", "PENDING"]);
const danger = new Set(["INACTIVE", "SUSPENDED", "OUT_OF_STOCK", "BLOCKED", "REJECTED", "CANCELLED"]);

export function StatusBadge({ value }: { value: string }) {
  const normalized = value.toUpperCase();
  const tone = positive.has(normalized)
    ? "success"
    : warning.has(normalized)
      ? "warning"
      : danger.has(normalized)
        ? "danger"
        : "neutral";
  return <span className={`status-badge status-${tone}`}>{humanize(normalized)}</span>;
}

export function RoleBadge({ value }: { value: string }) {
  return <span className="role-badge">{humanize(value)}</span>;
}
