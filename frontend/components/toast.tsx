"use client";

import { createContext, useCallback, useContext, useMemo, useState } from "react";
import { Icon } from "@/components/icon";

type ToastKind = "success" | "error" | "info";

interface ToastValue {
  showToast: (message: string, kind?: ToastKind) => void;
}

const ToastContext = createContext<ToastValue | null>(null);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toast, setToast] = useState<{ message: string; kind: ToastKind } | null>(null);
  const showToast = useCallback((message: string, kind: ToastKind = "success") => {
    setToast({ message, kind });
    window.setTimeout(() => setToast(null), 4200);
  }, []);
  const value = useMemo(() => ({ showToast }), [showToast]);
  return (
    <ToastContext.Provider value={value}>
      {children}
      {toast ? (
        <div className={`toast toast-${toast.kind}`} role="status" aria-live="polite">
          <Icon name={toast.kind === "error" ? "alert" : "check"} size={18} />
          <span>{toast.message}</span>
          <button type="button" onClick={() => setToast(null)} aria-label="Dismiss message">
            <Icon name="close" size={16} />
          </button>
        </div>
      ) : null}
    </ToastContext.Provider>
  );
}

export function useToast(): ToastValue {
  const value = useContext(ToastContext);
  if (!value) throw new Error("useToast must be used inside ToastProvider");
  return value;
}
