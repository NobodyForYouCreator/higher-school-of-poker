import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { wsBaseUrl } from "@/ui/lib/env";
import type { TableState, WsEnvelope } from "@/ui/poker/types";

type WsStatus = "idle" | "connecting" | "open" | "closed" | "error";

export function useTableSocket(tableId: string | null, token: string | null) {
  const [status, setStatus] = useState<WsStatus>("idle");
  const [state, setState] = useState<TableState | null>(null);
  const [lastError, setLastError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const connectIdRef = useRef(0);
  const openedRef = useRef(false);
  const attemptRef = useRef(0);

  const urls = useMemo(() => {
    if (!tableId || !token) return null;
    const base = wsBaseUrl().replace(/\/$/, "");
    const t = encodeURIComponent(token);
    const id = encodeURIComponent(tableId);
    // Some deployments mount ws under `/ws/...`, others under `/api/ws/...`.
    return [`${base}/ws/tables/${id}?token=${t}`, `${base}/api/ws/tables/${id}?token=${t}`];
  }, [tableId, token]);

  const disconnect = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
    setStatus("closed");
  }, []);

  const connect = useCallback(() => {
    if (!urls) return;
    connectIdRef.current += 1;
    const connectId = connectIdRef.current;
    openedRef.current = false;

    setStatus("connecting");
    setLastError(null);

    const url = urls[Math.min(attemptRef.current, urls.length - 1)];
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      if (connectId !== connectIdRef.current) return;
      openedRef.current = true;
      setStatus("open");
    };
    ws.onclose = (ev) => {
      if (connectId !== connectIdRef.current) return;
      if (!openedRef.current) {
        if (urls.length > 1 && attemptRef.current < urls.length - 1) {
          attemptRef.current += 1;
          // Retry immediately with the fallback path.
          connect();
          return;
        }
        setLastError(`WebSocket closed during connect (code ${ev.code}${ev.reason ? `: ${ev.reason}` : ""})`);
      }
      setStatus("closed");
    };
    ws.onerror = () => {
      if (connectId !== connectIdRef.current) return;
      setStatus("error");
      setLastError("WebSocket error");
    };
    ws.onmessage = (ev) => {
      if (connectId !== connectIdRef.current) return;
      try {
        const msg = JSON.parse(String(ev.data)) as WsEnvelope;
        const msgAny = msg as any;
        if (msgAny?.type === "table_state" && msgAny?.payload) {
          setState(msgAny.payload as TableState);
        } else if (msgAny?.type === "error") {
          const message = typeof msgAny?.message === "string" ? msgAny.message : "WebSocket error";
          const code = typeof msgAny?.code === "string" ? msgAny.code : null;
          setLastError(code ? `${code}: ${message}` : message);
        }
      } catch {
        // ignore
      }
    };
  }, [urls]);

  useEffect(() => {
    if (!urls) return;
    attemptRef.current = 0;
    connect();
    return () => disconnect();
  }, [connect, disconnect, urls]);

  const send = useCallback((payload: unknown) => {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return false;
    ws.send(JSON.stringify(payload));
    return true;
  }, []);

  const reconnect = useCallback(() => {
    attemptRef.current = 0;
    disconnect();
    window.setTimeout(() => connect(), 120);
  }, [connect, disconnect]);

  return { status, state, lastError, send, reconnect, disconnect };
}
