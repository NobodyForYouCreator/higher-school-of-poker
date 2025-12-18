import { useEffect, useMemo, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { ApiError } from "../lib/api/client";
import { tablesApi } from "../lib/api/tables";
import { tokenStorage } from "../lib/auth/tokenStorage";
import { connectTableWs } from "../lib/ws/tableWs";
import type { TableInfo } from "../types/api";
import type { TableState, WsServerMessage } from "../types/ws";

export function TablePage() {
  const { tableId } = useParams();

  const token = tokenStorage.get();
  const [tableInfo, setTableInfo] = useState<TableInfo | null>(null);
  const [tableState, setTableState] = useState<TableState | null>(null);
  const [wsStatus, setWsStatus] = useState<"disconnected" | "connecting" | "connected">(
    "disconnected"
  );
  const [error, setError] = useState<string | null>(null);
  const [raiseAmount, setRaiseAmount] = useState<number>(100);
  const [showAll, setShowAll] = useState(false);

  const wsRef = useRef<ReturnType<typeof connectTableWs> | null>(null);

  const canConnectWs = useMemo(() => Boolean(tableId && token), [tableId, token]);

  useEffect(() => {
    if (!tableId) return;

    let isActive = true;
    setError(null);

    (async () => {
      try {
        const info = await tablesApi.get(tableId);
        if (!isActive) return;
        setTableInfo(info);
      } catch (err) {
        if (!isActive) return;
        if (err instanceof ApiError) {
          setError("Не удалось загрузить стол. Проверь доступность API.");
        } else {
          setError("Не удалось загрузить стол.");
        }
      }
    })();

    return () => {
      isActive = false;
    };
  }, [tableId]);

  useEffect(() => {
    if (!canConnectWs || !tableId || !token) return;

    setWsStatus("connecting");
    setError(null);

    const connection = connectTableWs(tableId, token);
    wsRef.current = connection;

    connection.socket.addEventListener("open", () => setWsStatus("connected"));
    connection.socket.addEventListener("close", () => setWsStatus("disconnected"));
    connection.socket.addEventListener("error", () => {
      setWsStatus("disconnected");
      setError("WebSocket: ошибка подключения");
    });

    connection.onMessage((message: WsServerMessage) => {
      if (message.type === "table_state") {
        setTableState(message.payload);
        return;
      }
      if (message.type === "error") {
        setError(message.message);
      }
    });

    return () => {
      connection.socket.close();
      wsRef.current = null;
    };
  }, [canConnectWs, tableId, token]);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Стол</h1>
          <div className="mt-1 text-sm text-slate-400">ID: {tableId}</div>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            className="rounded-xl border border-slate-700 bg-slate-950/20 px-4 py-2 text-sm hover:bg-slate-900"
            type="button"
          >
            Выйти
          </button>
          <button
            className="rounded-xl bg-slate-50 px-4 py-2 text-sm font-medium text-slate-950 hover:bg-slate-200"
            type="button"
          >
            Наблюдать
          </button>
        </div>
      </div>

      {error ? (
        <div className="rounded-xl border border-red-900/60 bg-red-950/30 p-3 text-sm text-red-200">
          {error}
        </div>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
        <div className="rounded-2xl border border-emerald-900/50 bg-emerald-950/20 p-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="text-sm text-slate-300">Игровой стол</div>
            <div className="text-xs text-slate-500">
              WS: {wsStatus} · pot: {tableState?.pot ?? "—"} · phase:{" "}
              {tableState?.phase ?? "—"}
            </div>
          </div>

          <div className="mt-4 rounded-xl border border-slate-800 bg-slate-950/20 p-4">
            <div className="text-sm text-slate-300">Борд</div>
            <div className="mt-2 flex flex-wrap gap-2">
              {(tableState?.board ?? []).length === 0 ? (
                <div className="text-sm text-slate-500">—</div>
              ) : (
                tableState?.board.map((card, idx) => (
                  <div
                    className="rounded-lg border border-slate-700 bg-slate-950/30 px-3 py-2 text-sm"
                    key={`${card}-${idx}`}
                  >
                    {card}
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="mt-4 rounded-xl border border-slate-800 bg-slate-950/20 p-4">
            <div className="text-sm text-slate-300">Игроки</div>
            <div className="mt-2 grid gap-2 sm:grid-cols-2">
              {(tableState?.players ?? []).length === 0 ? (
                <div className="text-sm text-slate-500">—</div>
              ) : (
                tableState?.players.map((p) => (
                  <div
                    className="rounded-xl border border-slate-800 bg-slate-950/20 p-3"
                    key={p.user_id}
                  >
                    <div className="flex items-center justify-between gap-3">
                      <div className="text-sm font-medium">#{p.position}</div>
                      <div className="text-xs text-slate-500">{p.status}</div>
                    </div>
                    <div className="mt-2 text-sm text-slate-300">
                      stack: {p.stack} · bet: {p.bet}
                    </div>
                    <div className="mt-2 flex flex-wrap gap-2 text-xs text-slate-300">
                      {(p.hole_cards ?? []).map((c, idx) => (
                        <span
                          className="rounded-md border border-slate-700 bg-slate-950/30 px-2 py-1"
                          key={`${p.user_id}-${c}-${idx}`}
                        >
                          {c}
                        </span>
                      ))}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {tableInfo ? (
            <div className="mt-4 text-xs text-slate-500">
              Настройки: {tableInfo.private ? "private" : "public"} · max{" "}
              {tableInfo.max_players} · buy-in {tableInfo.buy_in}
            </div>
          ) : null}
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950/20 p-4">
          <div className="text-sm font-medium">Действия</div>
          <div className="mt-3 grid grid-cols-2 gap-2">
            <button
              className="rounded-xl border border-slate-700 bg-slate-950/20 px-3 py-2 text-sm hover:bg-slate-900"
              onClick={() => wsRef.current?.send({ type: "player_action", payload: { action: "fold" } })}
              type="button"
            >
              Fold
            </button>
            <button
              className="rounded-xl border border-slate-700 bg-slate-950/20 px-3 py-2 text-sm hover:bg-slate-900"
              onClick={() =>
                wsRef.current?.send({ type: "player_action", payload: { action: "check" } })
              }
              type="button"
            >
              Check
            </button>
            <button
              className="rounded-xl border border-slate-700 bg-slate-950/20 px-3 py-2 text-sm hover:bg-slate-900"
              onClick={() =>
                wsRef.current?.send({ type: "player_action", payload: { action: "call" } })
              }
              type="button"
            >
              Call
            </button>
            <button
              className="rounded-xl border border-slate-700 bg-slate-950/20 px-3 py-2 text-sm hover:bg-slate-900"
              onClick={() =>
                wsRef.current?.send({
                  type: "player_action",
                  payload: { action: "raise", amount: raiseAmount }
                })
              }
              type="button"
            >
              Raise
            </button>
          </div>

          <label className="mt-3 flex flex-col gap-1">
            <span className="text-xs text-slate-500">Raise amount</span>
            <input
              className="rounded-xl border border-slate-800 bg-slate-950/40 px-3 py-2 text-sm outline-none focus:border-slate-600"
              min={0}
              onChange={(e) => setRaiseAmount(Number(e.target.value))}
              type="number"
              value={raiseAmount}
            />
          </label>

          <label className="mt-4 flex items-center justify-between gap-3 rounded-xl border border-slate-800 bg-slate-950/20 px-3 py-2">
            <span className="text-sm text-slate-300">Показывать карты</span>
            <input
              checked={showAll}
              className="h-4 w-4"
              onChange={(e) => {
                const value = e.target.checked;
                setShowAll(value);
                wsRef.current?.send({ type: "toggle_show_all", payload: { show: value } });
              }}
              type="checkbox"
            />
          </label>
        </div>
      </div>
    </div>
  );
}
