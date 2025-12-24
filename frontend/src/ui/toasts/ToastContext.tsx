import React, { createContext, useCallback, useContext, useMemo, useState } from "react";

type Toast = {
  id: string;
  title: string;
  message?: string;
  tone?: "neutral" | "good" | "warn" | "bad";
};

type ToastInput = Omit<Toast, "id">;

type ToastContextValue = {
  push: (toast: ToastInput) => void;
};

const ToastContext = createContext<ToastContextValue | null>(null);

function toneBadge(tone?: Toast["tone"]) {
  if (tone === "good") return "badge badge-good";
  if (tone === "warn") return "badge badge-warn";
  if (tone === "bad") return "badge badge-bad";
  return "badge";
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const push = useCallback((toast: ToastInput) => {
    const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    const entry: Toast = { id, ...toast };
    setToasts((prev) => [entry, ...prev].slice(0, 4));
    window.setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4200);
  }, []);

  const value = useMemo(() => ({ push }), [push]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="toasts" aria-live="polite">
        {toasts.map((t) => (
          <div key={t.id} className="toast">
            <div className="row">
              <div className="toastTitle">{t.title}</div>
              <div className="spacer" />
              <span className={toneBadge(t.tone)} />
            </div>
            {t.message ? <div className="toastText">{t.message}</div> : null}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToasts() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToasts must be used within ToastProvider");
  return ctx;
}
