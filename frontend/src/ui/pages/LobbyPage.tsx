import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import Modal from "@/ui/components/Modal";
import { useAuth } from "@/ui/auth/AuthContext";
import { ApiError, apiGet, apiPost } from "@/ui/lib/http";
import type { TableSummary } from "@/ui/poker/types";
import { useToasts } from "@/ui/toasts/ToastContext";
import Button from "@/ui/kit/Button";
import Input from "@/ui/kit/Input";
import Badge from "@/ui/kit/Badge";
import { Panel, PanelBody, PanelHeader, PanelSubtitle, PanelTitle } from "@/ui/kit/Panel";

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
  const [query, setQuery] = useState("");

  const isAuthed = auth.status === "authed";

  const refresh = useCallback(async () => {
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
  }, [auth.token, toasts]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const emptyState = useMemo(() => {
    if (loading) return "Загружаем столы...";
    if (tables.length === 0) return "Пока нет столов. Создайте первый!";
    return null;
  }, [loading, tables.length]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const publicTables = tables.filter((t) => !t.private);
    if (!q) return publicTables;
    return publicTables.filter((t) => String(t.id).includes(q));
  }, [query, tables]);

  const queryAsId = useMemo(() => {
    const q = query.trim();
    if (!q) return null;
    if (!/^\d+$/.test(q)) return null;
    return q;
  }, [query]);

  return (
    <div className="pageGrid">
      <Panel>
        <PanelHeader>
          <div>
            <PanelTitle>Лобби</PanelTitle>
            <PanelSubtitle>Выберите стол или создайте новый</PanelSubtitle>
          </div>
          <div className="row wrap">
            {isAuthed ? (
              <Badge className="mono" tone="good">
                {auth.user?.balance ?? 0} фишек
              </Badge>
            ) : (
              <Badge tone="warn">Гость</Badge>
            )}
            <Button disabled={loading} onClick={() => void refresh()}>
              Обновить
            </Button>
            <Button
              variant="primary"
              onClick={() => {
                if (!isAuthed) {
                  navigate("/login");
                  return;
                }
                setShowCreate(true);
              }}
            >
              Создать стол
            </Button>
          </div>
        </PanelHeader>
        <PanelBody>
          <div className="row wrap">
            <div className="spacer" />
            <div className="fieldInline">
              <div className="fieldLabel">Поиск</div>
              <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="id стола" />
            </div>
          </div>

          <div className="tableList">
            {queryAsId ? (
              <div className="callout">
                <div>
                  <div className="calloutTitle">Приватный стол</div>
                  <div className="calloutText">Можно зайти напрямую по id: {queryAsId}</div>
                </div>
                <div className="spacer" />
                <Button
                  variant="primary"
                  onClick={() => {
                    if (!isAuthed) navigate("/login", { state: { from: `/tables/${queryAsId}` } });
                    else navigate(`/tables/${queryAsId}`);
                  }}
                >
                  Открыть
                </Button>
              </div>
            ) : null}
            {emptyState ? <div className="muted">{emptyState}</div> : null}
            {filtered.map((t) => (
              <div key={t.id} className="tableCard">
                <div className="tableCardMain">
                  <div className="tableCardTitle">Стол #{t.id}</div>
                  <div className="tableCardMeta">
                    <Badge tone={t.private ? "warn" : "neutral"}>{t.private ? "Приватный" : "Публичный"}</Badge>
                    <Badge className="mono">Buy-in: {t.buy_in}</Badge>
                    <Badge>
                      Игроки: {t.players_count}/{t.max_players}
                    </Badge>
                    <Badge>Зрители: {t.spectators_count}</Badge>
                  </div>
                </div>
                <div className="tableCardSide">
                  <div className="hint">Блайнды</div>
                  <div className="mono">SB 50 · BB 100</div>
                </div>
                <div className="tableCardActions">
                  <Button
                    onClick={() => {
                      if (!isAuthed) navigate("/login", { state: { from: `/tables/${t.id}` } });
                      else navigate(`/tables/${t.id}`);
                    }}
                  >
                    Открыть
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </PanelBody>
      </Panel>

      <Panel>
        <PanelHeader>
          <PanelTitle>Подсказки</PanelTitle>
          <Badge>Игровая логика</Badge>
        </PanelHeader>
        <PanelBody>
          <div className="noteList">
            <div className="note">Раздача стартует автоматически, когда за столом минимум 2 игрока.</div>
            <div className="note">Если вы зритель, можно включить показ карт.</div>
            <div className="note">Если вы закрыли вкладку, сервер уберёт вас со стола спустя небольшую паузу.</div>
          </div>
          {!isAuthed ? (
            <div className="callout">
              <div>
                <div className="calloutTitle">Нужен аккаунт</div>
                <div className="calloutText">Чтобы сесть за стол, нужно войти.</div>
              </div>
              <div className="spacer" />
              <Button variant="primary" onClick={() => navigate("/login")}>
                Войти
              </Button>
            </div>
          ) : null}
        </PanelBody>
      </Panel>

      {showCreate ? (
        <Modal title="Создать стол" onClose={() => setShowCreate(false)}>
          <form
            className="form"
            onSubmit={(e) => {
              e.preventDefault();
              void (async () => {
                try {
                  const created = await apiPost<TableSummary, CreatePayload>("/tables/create", create, auth.token);
                  setShowCreate(false);
                  toasts.push({ title: "Стол создан", message: `Стол #${created.id}`, tone: "good" });
                  await refresh();
                  navigate(`/tables/${created.id}`);
                } catch (err) {
                  const msg = err instanceof ApiError ? err.message : "Не удалось создать стол";
                  toasts.push({ title: "Ошибка", message: msg, tone: "bad" });
                }
              })();
            }}
          >
            <label className="field">
              <div className="fieldLabel">Max players (2..9)</div>
              <Input
                className="mono"
                value={create.max_players}
                type="number"
                min={2}
                max={9}
                onChange={(e) => setCreate((p) => ({ ...p, max_players: Number(e.target.value) }))}
              />
            </label>
            <label className="field">
              <div className="fieldLabel">Buy-in</div>
              <Input
                className="mono"
                value={create.buy_in}
                type="number"
                min={0}
                onChange={(e) => setCreate((p) => ({ ...p, buy_in: Number(e.target.value) }))}
              />
            </label>
            <label className="toggleRow">
              <input
                type="checkbox"
                checked={create.private}
                onChange={(e) => setCreate((p) => ({ ...p, private: e.target.checked }))}
              />
              <span>Приватный стол</span>
            </label>
            <div className="row wrap">
              <Button
                variant="primary"
                type="submit"
              >
                Создать
              </Button>
              <div className="spacer" />
              <Button onClick={() => setShowCreate(false)}>Отмена</Button>
            </div>
          </form>
        </Modal>
      ) : null}
    </div>
  );
}
