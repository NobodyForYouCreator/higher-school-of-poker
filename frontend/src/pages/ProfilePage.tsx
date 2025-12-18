import { useEffect, useState } from "react";
import { ApiError } from "../lib/api/client";
import { statsApi } from "../lib/api/stats";
import type { HandHistoryItem, PlayerStats } from "../types/api";

export function ProfilePage() {
  const [stats, setStats] = useState<PlayerStats | null>(null);
  const [history, setHistory] = useState<HandHistoryItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;
    setError(null);

    (async () => {
      try {
        const [statsRes, historyRes] = await Promise.all([
          statsApi.myStats(),
          statsApi.myHistory()
        ]);
        if (!isActive) return;
        setStats(statsRes);
        setHistory(historyRes);
      } catch (err) {
        if (!isActive) return;
        if (err instanceof ApiError) {
          setError("Не удалось загрузить профиль. Проверь доступность API.");
        } else {
          setError("Не удалось загрузить профиль.");
        }
      }
    })();

    return () => {
      isActive = false;
    };
  }, []);

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-semibold">Профиль</h1>

      {error ? (
        <div className="rounded-xl border border-red-900/60 bg-red-950/30 p-3 text-sm text-red-200">
          {error}
        </div>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-2xl border border-slate-800 bg-slate-950/20 p-4">
          <div className="text-sm font-medium">Статистика</div>
          <div className="mt-3 grid grid-cols-2 gap-2 text-sm text-slate-300">
            <div className="rounded-xl border border-slate-800 bg-slate-950/20 p-3">
              Победы: {stats?.hands_won ?? "—"}
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-950/20 p-3">
              Поражения: {stats?.hands_lost ?? "—"}
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-950/20 p-3">
              Макс. баланс: {stats?.max_balance ?? "—"}
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-950/20 p-3">
              Макс. ставка: {stats?.max_bet ?? "—"}
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950/20 p-4">
          <div className="text-sm font-medium">История</div>
          <div className="mt-3 grid gap-2">
            {(history ?? []).length === 0 ? (
              <div className="text-sm text-slate-500">—</div>
            ) : (
              history?.map((h) => (
                <div
                  className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-800 bg-slate-950/20 p-3 text-sm text-slate-300"
                  key={h.id}
                >
                  <div>
                    <div className="font-medium">{h.result ?? "hand"}</div>
                    <div className="mt-1 text-xs text-slate-500">
                      table: {h.table_id ?? "—"} · pot: {h.pot ?? "—"}
                    </div>
                  </div>
                  <div className="text-xs text-slate-500">{h.finished_at ?? ""}</div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
