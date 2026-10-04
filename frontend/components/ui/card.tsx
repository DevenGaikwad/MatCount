import type { ReactNode } from "react";
import { Icon } from "@/components/icon";

export function Panel({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return <section className={`panel ${className}`}>{children}</section>;
}

export function MetricCard({
  label,
  value,
  support,
  icon = "reports",
}: {
  label: string;
  value: string;
  support?: string;
  icon?: string;
}) {
  return (
    <article className="metric-card">
      <div className="metric-icon"><Icon name={icon} size={20} /></div>
      <div>
        <p>{label}</p>
        <strong>{value}</strong>
        {support ? <span>{support}</span> : null}
      </div>
    </article>
  );
}
