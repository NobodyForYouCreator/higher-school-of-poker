import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { tablesApi } from "../lib/api/tables";
import { ApiError } from "../lib/api/client";
import type { TableInfo, TableSummary } from "../types/api";

export function LobbyPage() {
  const navigate = useNavigate();
  const [tables, setTables] = useState<TableSummary[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canShowList = useMemo(() => Array.isArray(tables), [tables]);

  async function loadTables() {
    setIsLoading(true);
    setError(null);

    try {
      const list = await tablesApi.list();
      setTables(list);
    } catch (err) {
      if (err instanceof ApiError) {
        setError("Не удалось загрузить столы. Проверь доступность API.");
      } else {
        setError("Не удалось загрузить столы.");
      }
      setTables([]);
    } finally {
      setIsLoading(false);
    }
  }

  async function quickCreate() {
    setIsLoading(true);
    setError(null);

    try {
      const created: TableInfo = await tablesApi.create({
        max_players: 6,
        private: false,
        buy_in: 1000
      });
      navigate(`/tables/${created.id}`);
    } catch (err) {
      if (err instanceof ApiError) {
        setError("Не удалось создать стол. Проверь доступность API.");
      } else {
        setError("Не удалось создать стол.");
      }
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadTables();
  }, []);

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">Лобби</h1>
        <div className="flex flex-wrap gap-2">
          <button
            className="rounded-xl border border-slate-700 bg-slate-950/20 px-4 py-2 text-sm hover:bg-slate-900 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={isLoading}
            onClick={() => void loadTables()}
            type="button"
          >
            Обновить
          </button>
          <button
            className="rounded-xl bg-slate-50 px-4 py-2 text-sm font-medium text-slate-950 hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={isLoading}
            onClick={() => void quickCreate()}
            type="button"
          >
            Создать стол
          </button>
        </div>
      </div>

      {error ? (
        <div className="rounded-xl border border-red-900/60 bg-red-950/30 p-3 text-sm text-red-200">
          {error}
        </div>
      ) : null}

      <div className="grid gap-3">
        {isLoading && !canShowList ? (
          <div className="rounded-xl border border-slate-800 bg-slate-950/20 p-4 text-slate-300">
            Загружаем столы...
          </div>
        ) : null}

        {canShowList && (tables?.length ?? 0) === 0 ? (
          <div className="rounded-xl border border-slate-800 bg-slate-950/20 p-4 text-slate-300">
            Пока нет столов. Создай первый.
          </div>
        ) : null}

        {tables?.map((table) => (
          <div
            className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-slate-800 bg-slate-950/20 p-4"
            key={table.id}
          >
            <div>
              <div className="font-medium">Стол</div>
              <div className="mt-1 text-xs text-slate-500">{table.id}</div>
              <div className="mt-2 text-sm text-slate-300">
                {table.private ? "Приватный" : "Публичный"} ·{" "}
                {table.players_count ?? "?"}/{table.max_players} · buy-in{" "}
                {table.buy_in}
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              <Link
                className="rounded-xl border border-slate-700 bg-slate-950/20 px-4 py-2 text-sm hover:bg-slate-900"
                to={`/tables/${table.id}`}
              >
                Открыть
              </Link>
              <button
                className="rounded-xl bg-emerald-500 px-4 py-2 text-sm font-medium text-emerald-950 hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60"
                disabled={isLoading}
                onClick={async () => {
                  try {
                    await tablesApi.join(table.id);
                    navigate(`/tables/${table.id}`);
                  } catch {
                    navigate(`/tables/${table.id}`);
                  }
                }}
                type="button"
              >
                Сесть
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
