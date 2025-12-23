import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "@/ui/auth/AuthContext";
import { ApiError, apiGet, apiPostEmpty } from "@/ui/lib/http";
import type { TableInfo, TableState } from "@/ui/poker/types";
import { useTableSocket } from "@/ui/poker/useTableSocket";
import { useToasts } from "@/ui/toasts/ToastContext";
import TableStage from "@/ui/poker/TableStage";
import { useUsernames } from "@/ui/poker/useUsernames";

type JoinRole = "player" | "spectator";

function myPlayerState(state: TableState | null, myId: number | null) {
  if (!state || !myId) return null;
  return state.players.find((p) => p.user_id === myId) ?? null;
}

export default function TablePage() {
  const auth = useAuth();
  const toasts = useToasts();
  const navigate = useNavigate();
  const { tableId } = useParams();

  const [info, setInfo] = useState<TableInfo | null>(null);
  const [role, setRole] = useState<JoinRole>("player");
  const [showAll, setShowAll] = useState(false);
  const [betAmount, setBetAmount] = useState(200);

  const isAuthed = auth.status === "authed";
  const { status: wsStatus, state, lastError, send, reconnect } = useTableSocket(tableId ?? null, auth.token);
  const { displayName, ensure: ensureNames } = useUsernames(auth.token);

  const refreshInfo = useCallback(async () => {
    if (!tableId) return;
    try {
      const data = await apiGet<TableInfo>(`/tables/${tableId}`, auth.token);
      setInfo(data);
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : "Не удалось загрузить стол";
      toasts.push({ title: "Ошибка", message: msg, tone: "bad" });
    }
  }, [auth.token, tableId, toasts]);

  useEffect(() => {
    void refreshInfo();
  }, [refreshInfo]);

  useEffect(() => {
    if (!lastError) return;
    toasts.push({ title: "WS", message: lastError, tone: "warn" });
  }, [lastError, toasts]);

  const myId = auth.user?.id ?? null;
  const mySeat = useMemo(() => (info && myId ? info.seats.find((s) => s.user_id === myId) ?? null : null), [info, myId]);
  const iAmSpectator = mySeat?.is_spectator ?? false;
  const iAmSeated = Boolean(mySeat);

  const myState = useMemo(() => myPlayerState(state, myId), [myId, state]);
  const currentBet = state?.current_bet ?? null;
  const myBet = myState?.bet ?? 0;
  const toCall = currentBet !== null ? Math.max(0, currentBet - myBet) : 0;
  const isMyTurn = Boolean(state?.current_player_id && myId && state.current_player_id === myId);

  const minBet = state?.min_bet ?? 100;

  const canAct = isAuthed && iAmSeated && !iAmSpectator && wsStatus === "open";
  const canToggleShowAll = isAuthed && iAmSpectator && wsStatus === "open";

  useEffect(() => {
    const ids = new Set<number>();
    if (myId) ids.add(myId);
    for (const p of state?.players ?? []) ids.add(p.user_id);
    for (const w of state?.winners ?? []) ids.add(w);
    if (info) {
      for (const s of info.seats) ids.add(s.user_id);
    }
    void ensureNames(Array.from(ids));
  }, [ensureNames, info, myId, state?.players, state?.winners]);

  useEffect(() => {
    if (!iAmSpectator && showAll) setShowAll(false);
  }, [iAmSpectator, showAll]);

  const lastWinnersKeyRef = useRef<string>("");
  useEffect(() => {
    const winners = state?.winners ?? [];
    if (!Array.isArray(winners) || winners.length === 0) return;
    if (state?.phase !== "finished") return;
    const key = winners.slice().sort((a, b) => a - b).join(",");
    if (key && lastWinnersKeyRef.current === key) return;
    lastWinnersKeyRef.current = key;
    toasts.push({
      title: "Раздача завершена",
      message: `Победил(и): ${winners.map((x) => displayName(x)).join(", ")}`,
      tone: "good",
    });
  }, [displayName, state?.phase, state?.winners, toasts]);

  const action = useCallback(
    (type: string, amount?: number) => {
      const ok = send({ type: "player_action", payload: { action: type, amount } });
      if (!ok) toasts.push({ title: "WS", message: "Соединение не готово", tone: "warn" });
    },
    [send, toasts],
  );

  if (!tableId) return null;

  return (
    <div style={{ display: "grid", gap: 16 }}>
      <div className="panel">
        <div className="panelHeader">
          <div>
            <div className="panelTitle">Стол #{tableId}</div>
            <div className="hint">
              WS: <span className="mono">{wsStatus}</span> · {iAmSeated ? (iAmSpectator ? "режим зрителя" : "игрок") : "не за столом"}
            </div>
          </div>
          <div className="row" style={{ flexWrap: "wrap" }}>
            {state ? <span className="badge mono">Пот: {state.pot}</span> : null}
            <button className="btn" onClick={() => void refreshInfo()}>
              Обновить
            </button>
            <button className="btn" onClick={() => reconnect()}>
              Переподключить WS
            </button>
            <button className="btn btnGhost" onClick={() => navigate("/")}>
              В лобби
            </button>
          </div>
        </div>
        <div className="panelBody" style={{ display: "grid", gap: 14 }}>
          {!isAuthed ? (
            <div className="row" style={{ flexWrap: "wrap" }}>
              <span className="muted">Чтобы играть или наблюдать, нужно войти.</span>
              <button className="btn btnPrimary" onClick={() => navigate("/login")}>
                Войти
              </button>
            </div>
          ) : (
            <div className="row" style={{ flexWrap: "wrap" }}>
              <span className="badge">
                Мест: {info ? info.players_count : "—"}/{info ? info.max_players : "—"}
              </span>
              <span className="badge">Buy-in: {info ? info.buy_in : "—"}</span>
              {iAmSeated ? <span className="badge badgeGood">Вы за столом</span> : <span className="badge badgeWarn">Вы не за столом</span>}
              <div className="spacer" />
              <select className="input" style={{ width: 200 }} value={role} onChange={(e) => setRole(e.target.value as JoinRole)}>
                <option value="player">Сесть игроком</option>
                <option value="spectator">Зайти зрителем</option>
              </select>
              <button
                className="btn btnPrimary"
                disabled={!info}
                onClick={async () => {
                  try {
                    if (role === "player") await apiPostEmpty(`/tables/${tableId}/join`, auth.token);
                    else await apiPostEmpty(`/tables/${tableId}/spectate`, auth.token);
                    await refreshInfo();
                    reconnect();
                    toasts.push({ title: "Готово", message: role === "player" ? "Вы сели за стол." : "Вы в режиме зрителя.", tone: "good" });
                  } catch (e) {
                    const msg = e instanceof ApiError ? e.message : "Не удалось выполнить действие";
                    toasts.push({ title: "Ошибка", message: msg, tone: "bad" });
                  }
                }}
              >
                Войти
              </button>
              <button
                className="btn btnDanger"
                disabled={!iAmSeated}
                onClick={async () => {
                  try {
                    await apiPostEmpty(`/tables/${tableId}/leave`, auth.token);
                    await refreshInfo();
                    reconnect();
                    toasts.push({ title: "Вы вышли со стола", tone: "neutral" });
                  } catch (e) {
                    const msg = e instanceof ApiError ? e.message : "Не удалось покинуть стол";
                    toasts.push({ title: "Ошибка", message: msg, tone: "bad" });
                  }
                }}
              >
                Выйти
              </button>
            </div>
          )}
        </div>
      </div>

      {state ? (
        <TableStage state={state} myId={myId} maxPlayers={info?.max_players ?? 6} displayName={displayName} />
      ) : (
        <div className="panel">
          <div className="panelHeader">
            <div className="panelTitle">Стол</div>
            <span className="badge">ожидание состояния</span>
          </div>
          <div className="panelBody">
            <div className="muted">
              {wsStatus === "open" ? "Подключено. Ждём данные..." : "Подключаемся к WS..."}
              <div className="hint">Если WS не подключается — проверьте, что backend запущен на 8000 и вы вошли.</div>
            </div>
          </div>
        </div>
      )}

      <div className="panel">
        <div className="panelHeader">
          <div className="panelTitle">Действия</div>
          <div className="row" style={{ flexWrap: "wrap" }}>
            {state ? <span className="badge mono">Пот: {state.pot}</span> : null}
            <span className="badge">Ход: {isMyTurn ? "ваш" : "не ваш"}</span>
            {iAmSpectator ? <span className="badge badgeWarn">Вы зритель</span> : null}
          </div>
        </div>
        <div className="panelBody">
          <div className="actionPanel">
            <div className="actionRow">
              <div className="row" style={{ gap: 10, flexWrap: "wrap" }}>
                <span className="badge mono">to call: {toCall}</span>
                <span className="badge mono">min bet: {minBet}</span>
              </div>
              <div className="row" style={{ gap: 10, flexWrap: "wrap" }}>
                {iAmSpectator ? (
                  <button
                    className="btn"
                    disabled={!canToggleShowAll}
                    onClick={() => {
                      const next = !showAll;
                      setShowAll(next);
                      const ok = send({ type: "toggle_show_all", payload: { show: next } });
                      if (!ok) toasts.push({ title: "WS", message: "Соединение не готово", tone: "warn" });
                    }}
                  >
                    {showAll ? "Скрыть карты" : "Показывать карты"}
                  </button>
                ) : (
                  <span className="badge">Показывать карты: только для зрителей</span>
                )}
              </div>
            </div>

            <div className="actionRow2">
              <button className="btn" disabled={!canAct || !isMyTurn} onClick={() => action("fold")}>
                Fold
              </button>
              <button className="btn" disabled={!canAct || !isMyTurn} onClick={() => action("check")}>
                Check
              </button>
              <button className="btn btnPrimary" disabled={!canAct || !isMyTurn} onClick={() => action("call", toCall)}>
                Call {toCall > 0 ? `(${toCall})` : ""}
              </button>
              <button className="btn" disabled={!canAct || !isMyTurn} onClick={() => action("all_in")}>
                All-in
              </button>
              <div className="spacer" />
              <div className="row" style={{ gap: 10, flexWrap: "wrap" }}>
                <input
                  className="range"
                  type="range"
                  min={minBet}
                  max={Math.max(minBet, (myState?.stack ?? 0) + (myState?.bet ?? 0))}
                  value={betAmount}
                  onChange={(e) => setBetAmount(Number(e.target.value))}
                />
                <input
                  className="input mono"
                  style={{ width: 120 }}
                  value={betAmount}
                  type="number"
                  min={0}
                  onChange={(e) => setBetAmount(Number(e.target.value))}
                />
                <button
                  className="btn"
                  disabled={!canAct || !isMyTurn}
                  onClick={() => action(currentBet && currentBet > 0 ? "raise" : "bet", betAmount)}
                >
                  {currentBet && currentBet > 0 ? "Raise" : "Bet"}
                </button>
              </div>
            </div>

            {!state?.current_player_id && iAmSeated && !iAmSpectator ? (
              <div className="hint">
                Раздача ещё не началась. Первый корректный ход запускает её. Если нужно, нажмите{" "}
                <button
                  className="btn btnGhost"
                  onClick={() => {
                    send({ type: "player_action", payload: { action: "check", amount: 0 } });
                    reconnect();
                  }}
                >
                  «Подтянуть состояние»
                </button>
                .
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
