import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import Modal from "@/ui/components/Modal";
import { useAuth } from "@/ui/auth/AuthContext";
import { ApiError, apiGet, apiPost } from "@/ui/lib/http";
import type { TableSummary } from "@/ui/poker/types";
import { useToasts } from "@/ui/toasts/ToastContext";

type CreatePayload = {
  max_players: number;
  buy_in: number;
  private: boolean;
};

export default function LobbyPage() {
  const auth = useAuth();
  const toasts = useToasts();
  const navigate = useNavigate();

  const [tables, setTables] = useState<TableSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [create, setCreate] = useState<CreatePayload>({ max_players: 6, buy_in: 5000, private: false });

  const canUseTables = auth.status === "authed";

  const refresh = useCallback(async () => {
    if (!canUseTables) return;
    setLoading(true);
    try {
      const list = await apiGet<TableSummary[]>("/tables", auth.token);
      setTables(list);
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : "Не удалось загрузить столы";
      toasts.push({ title: "Ошибка", message: msg, tone: "bad" });
    } finally {
      setLoading(false);
    }
  }, [auth.token, canUseTables, toasts]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const emptyState = useMemo(() => {
    if (loading) return "Загружаем столы...";
    if (tables.length === 0) return "Пока нет столов. Создайте первый!";
    return null;
  }, [loading, tables.length]);

  return (
    <div className="grid2">
      <div className="panel">
        <div className="panelHeader">
          <div>
            <div className="panelTitle">Лобби</div>
            <div className="hint">Выберите стол или создайте новый</div>
          </div>
          <div className="row">
            <button className="btn" disabled={!canUseTables || loading} onClick={() => void refresh()}>
              Обновить
            </button>
            <button
              className="btn btnPrimary"
              disabled={!canUseTables}
              onClick={() => {
                if (!canUseTables) {
                  navigate("/login");
                  return;
                }
                setShowCreate(true);
              }}
            >
              Создать стол
            </button>
          </div>
        </div>
        <div className="panelBody">
          {auth.status !== "authed" ? (
            <div className="muted">
              Для просмотра и создания столов нужно войти.{" "}
              <button className="btn btnPrimary" onClick={() => navigate("/login")}>
                Войти
              </button>
            </div>
          ) : (
            <div className="tableList">
              {emptyState ? <div className="muted">{emptyState}</div> : null}
              {tables.map((t) => (
                <div key={t.id} className="tableRow">
                  <div>
                    <div className="tableName">Стол #{t.id}</div>
                    <div className="tableMeta">
                      <span className="badge">{t.private ? "Приватный" : "Публичный"}</span>
                      <span className="badge">Buy-in: {t.buy_in}</span>
                      <span className="badge">
                        Игроки: {t.players_count}/{t.max_players}
                      </span>
                      <span className="badge">Зрители: {t.spectators_count}</span>
                    </div>
                  </div>

                  <div className="muted">
                    <div className="hint">Вход</div>
                    <div>Через WS на столе</div>
                  </div>
                  <div className="muted">
                    <div className="hint">Ставки</div>
                    <div className="mono">BB: 100</div>
                  </div>

                  <div className="row" style={{ justifyContent: "flex-end", gap: 10 }}>
                    <button className="btn" onClick={() => navigate(`/tables/${t.id}`)}>
                      Открыть
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="panel">
        <div className="panelHeader">
          <div className="panelTitle">Советы</div>
          <span className="badge">UX</span>
        </div>
        <div className="panelBody">
          <div className="muted" style={{ lineHeight: 1.6 }}>
            <div>• Хотите видеть все карты? Зайдите на стол зрителем и включите «Показывать карты».</div>
            <div>• Если раздача ещё не началась — первый ход запускает её автоматически.</div>
            <div>• Если вы закрыли вкладку стола, сервер автоматически убирает вас со стола.</div>
          </div>
        </div>
      </div>

      {showCreate ? (
        <Modal title="Создать стол" onClose={() => setShowCreate(false)}>
          <div style={{ display: "grid", gap: 12 }}>
            <label>
              <div className="hint">Max players (2..9)</div>
              <input
                className="input mono"
                value={create.max_players}
                type="number"
                min={2}
                max={9}
                onChange={(e) => setCreate((p) => ({ ...p, max_players: Number(e.target.value) }))}
              />
            </label>
            <label>
              <div className="hint">Buy-in</div>
              <input
                className="input mono"
                value={create.buy_in}
                type="number"
                min={0}
                onChange={(e) => setCreate((p) => ({ ...p, buy_in: Number(e.target.value) }))}
              />
            </label>
            <label className="row" style={{ alignItems: "center", gap: 10 }}>
              <input
                type="checkbox"
                checked={create.private}
                onChange={(e) => setCreate((p) => ({ ...p, private: e.target.checked }))}
              />
              <span>Приватный стол</span>
            </label>
            <div className="row">
              <button
                className="btn btnPrimary"
                onClick={async () => {
                  try {
                    const created = await apiPost<TableSummary, CreatePayload>("/tables/create", create, auth.token);
                    setShowCreate(false);
                    toasts.push({ title: "Стол создан", message: `Стол #${created.id}`, tone: "good" });
                    await refresh();
                    navigate(`/tables/${created.id}`);
                  } catch (e) {
                    const msg = e instanceof ApiError ? e.message : "Не удалось создать стол";
                    toasts.push({ title: "Ошибка", message: msg, tone: "bad" });
                  }
                }}
              >
                Создать
              </button>
              <div className="spacer" />
              <button className="btn" onClick={() => setShowCreate(false)}>
                Отмена
              </button>
            </div>
          </div>
        </Modal>
      ) : null}
    </div>
  );
}

