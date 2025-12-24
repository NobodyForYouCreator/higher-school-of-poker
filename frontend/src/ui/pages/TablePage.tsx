import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "@/ui/auth/AuthContext";
import { ApiError, apiGet, apiPostEmpty } from "@/ui/lib/http";
import type { TableInfo, TableState } from "@/ui/poker/types";
import { useTableSocket } from "@/ui/poker/useTableSocket";
import { useToasts } from "@/ui/toasts/ToastContext";
import TableStage from "@/ui/poker/TableStage";
import { useUsernames } from "@/ui/poker/useUsernames";
import Badge from "@/ui/kit/Badge";
import Button from "@/ui/kit/Button";
import Input from "@/ui/kit/Input";
import { Panel, PanelBody, PanelHeader, PanelSubtitle, PanelTitle } from "@/ui/kit/Panel";

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
  const [showAll, setShowAll] = useState(false);
  const [betAmount, setBetAmount] = useState(200);

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
    toasts.push({ title: "Соединение", message: lastError, tone: "warn" });
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
  const maxBet = useMemo(() => Math.max(minBet, (myState?.stack ?? 0) + (myState?.bet ?? 0)), [minBet, myState?.bet, myState?.stack]);
  useEffect(() => {
    if (betAmount < minBet) setBetAmount(minBet);
    if (betAmount > maxBet) setBetAmount(maxBet);
  }, [betAmount, maxBet, minBet]);

  const canAct = iAmSeated && !iAmSpectator && wsStatus === "open" && Boolean(state?.hand_active);
  const canToggleShowAll = iAmSpectator && wsStatus === "open";

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
      if (!ok) toasts.push({ title: "Соединение", message: "Соединение не готово", tone: "warn" });
    },
    [send, toasts],
  );

  if (!tableId) return null;

  return (
    <div className="tablePage">
      <Panel>
        <PanelHeader>
          <div>
            <PanelTitle>Стол #{tableId}</PanelTitle>
            <PanelSubtitle>
              <span className="row wrap">
                {iAmSeated ? <Badge tone={iAmSpectator ? "warn" : "good"}>{iAmSpectator ? "зритель" : "игрок"}</Badge> : <Badge>не за столом</Badge>}
                {info ? (
                  <>
                    <Badge>Игроков: {info.players_count}/{info.max_players}</Badge>
                    <Badge className="mono">Вход: {info.buy_in}</Badge>
                    {info.private ? <Badge tone="warn">Приватный</Badge> : null}
                  </>
                ) : null}
              </span>
            </PanelSubtitle>
          </div>

          <div className="row wrap">
            {lastError ? (
              <Badge tone="warn" className="mono">
                {lastError}
              </Badge>
            ) : null}
            <Button onClick={() => navigate("/")}>В лобби</Button>
            <Button onClick={() => void refreshInfo()}>Обновить</Button>
            <Button onClick={() => reconnect()}>Переподключить</Button>
          </div>
        </PanelHeader>

        <PanelBody>
          <div className="tableLayout">
            <div className="tableStageWrap">
              {state ? (
                <TableStage state={state} myId={myId} maxPlayers={info?.max_players ?? 6} displayName={displayName} />
              ) : (
                <div className="emptyCard">
                  <div className="emptyTitle">Ожидание состояния</div>
                  <div className="emptyText">{wsStatus === "open" ? "Подключено. Ждём данные..." : "Подключаемся к WebSocket..."}</div>
                </div>
              )}
            </div>

            <div className="tableSidebar">
              <Panel className="subPanel">
                <PanelHeader>
                  <PanelTitle>Место</PanelTitle>
                  <Badge className="mono" tone="good">
                    {auth.user?.balance ?? 0} фишек
                  </Badge>
                </PanelHeader>
                <PanelBody>
                  {!iAmSeated ? (
                    <div className="stack">
                      <div className="row wrap">
                        <Button
                          variant="primary"
                          onClick={async () => {
                            try {
                              await apiPostEmpty(`/tables/${tableId}/join`, auth.token);
                              await refreshInfo();
                              await auth.refreshMe();
                              toasts.push({ title: "Вы за столом", message: "Вы вошли как игрок.", tone: "good" });
                            } catch (e) {
                              const msg = e instanceof ApiError ? e.message : "Не удалось присоединиться";
                              toasts.push({ title: "Ошибка", message: msg, tone: "bad" });
                            }
                          }}
                        >
                          Игрок
                        </Button>
                        <Button
                          onClick={async () => {
                            try {
                              await apiPostEmpty(`/tables/${tableId}/spectate`, auth.token);
                              await refreshInfo();
                              toasts.push({ title: "Вы за столом", message: "Вы вошли как зритель.", tone: "good" });
                            } catch (e) {
                              const msg = e instanceof ApiError ? e.message : "Не удалось присоединиться";
                              toasts.push({ title: "Ошибка", message: msg, tone: "bad" });
                            }
                          }}
                        >
                          Зритель
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="stack">
                      <div className="row wrap">
                        <Badge tone={iAmSpectator ? "warn" : "good"}>{iAmSpectator ? "Зритель" : "Игрок"}</Badge>
                        {myState ? (
                          <>
                            <Badge className="mono">В игре: {myState.stack}</Badge>
                            {myState.bet > 0 ? <Badge className="mono">Ставка: {myState.bet}</Badge> : null}
                          </>
                        ) : null}
                      </div>
                      {iAmSpectator ? (
                        <Button
                          disabled={!canToggleShowAll}
                          onClick={() => {
                            const next = !showAll;
                            setShowAll(next);
                            const ok = send({ type: "toggle_show_all", payload: { show: next } });
                            if (!ok) toasts.push({ title: "Соединение", message: "Соединение не готово", tone: "warn" });
                          }}
                        >
                          {showAll ? "Скрыть карты" : "Показывать карты"}
                        </Button>
                      ) : null}
                      <Button
                        variant="danger"
                        onClick={async () => {
                          try {
                            await apiPostEmpty(`/tables/${tableId}/leave`, auth.token);
                            await refreshInfo();
                            await auth.refreshMe();
                            toasts.push({ title: "Вы вышли", message: "Место освобождено.", tone: "good" });
                          } catch (e) {
                            const msg = e instanceof ApiError ? e.message : "Не удалось покинуть стол";
                            toasts.push({ title: "Ошибка", message: msg, tone: "bad" });
                          }
                        }}
                      >
                        Покинуть стол
                      </Button>
                    </div>
                  )}
                </PanelBody>
              </Panel>

              <Panel className="subPanel">
                <PanelHeader>
                  <PanelTitle>Действия</PanelTitle>
                  <div className="row wrap">
                    <Badge tone={isMyTurn ? "good" : "neutral"}>{isMyTurn ? "Ваш ход" : "Ожидание"}</Badge>
                    {state ? <Badge className="mono">Банк: {state.pot}</Badge> : null}
                  </div>
                </PanelHeader>
                <PanelBody>
                  <div className="stack">
                    <div className="actionButtons">
                      <Button disabled={!canAct || !isMyTurn} onClick={() => action("fold")}>
                        Пас
                      </Button>
                      {toCall > 0 ? (
                        <Button variant="primary" disabled={!canAct || !isMyTurn} onClick={() => action("call", toCall)}>
                          Уравнять
                        </Button>
                      ) : (
                        <Button variant="primary" disabled={!canAct || !isMyTurn} onClick={() => action("check")}>
                          Чек
                        </Button>
                      )}
                      <Button disabled={!canAct || !isMyTurn} onClick={() => action("all_in")}>
                        Ва-банк
                      </Button>
                    </div>

                    <div className="betBox">
                      <div className="betRow">
                        <input
                          className="range"
                          type="range"
                          min={minBet}
                          max={maxBet}
                          value={betAmount}
                          onChange={(e) => setBetAmount(Number(e.target.value))}
                        />
                        <Input
                          className="mono"
                          value={betAmount}
                          type="number"
                          min={0}
                          onChange={(e) => setBetAmount(Number(e.target.value))}
                        />
                      </div>
                      <Button disabled={!canAct || !isMyTurn} onClick={() => action(currentBet && currentBet > 0 ? "raise" : "bet", betAmount)}>
                        {currentBet && currentBet > 0 ? "Повысить" : "Ставка"}
                      </Button>
                    </div>
                  </div>
                </PanelBody>
              </Panel>
            </div>
          </div>
        </PanelBody>
      </Panel>
    </div>
  );
}
