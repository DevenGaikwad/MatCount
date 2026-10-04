import { Icon } from "@/components/icon";
import { Button } from "@/components/ui/button";

export function LoadingState({ label = "Loading SEMS data…" }: { label?: string }) {
  return (
    <div className="state-card state-loading" role="status" aria-live="polite">
      <div className="skeleton-layout" aria-hidden="true">
        <span className="skeleton skeleton-title" />
        <span className="skeleton skeleton-line" />
        <span className="skeleton skeleton-line short" />
        <div className="skeleton-grid"><span /><span /><span /></div>
      </div>
      <strong>{label}</strong>
      <p>Preparing the latest information for your authorized scope.</p>
    </div>
  );
}

export function EmptyState({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="state-card">
      <div className="state-icon"><Icon name="inventory" size={24} /></div>
      <strong>{title}</strong>
      <p>{description}</p>
    </div>
  );
}

export function ErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div className="state-card state-error" role="alert">
      <div className="state-icon"><Icon name="alert" size={24} /></div>
      <strong>SEMS could not load this section</strong>
      <p>{message}</p>
      {onRetry ? <Button variant="secondary" onClick={onRetry}>Try again</Button> : null}
    </div>
  );
}
