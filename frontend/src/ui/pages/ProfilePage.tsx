import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useAuth } from "@/ui/auth/AuthContext";
import { ApiError, apiGet } from "@/ui/lib/http";
import { useToasts } from "@/ui/toasts/ToastContext";
import Badge from "@/ui/kit/Badge";
import Button from "@/ui/kit/Button";
import { Panel, PanelBody, PanelHeader, PanelSubtitle, PanelTitle } from "@/ui/kit/Panel";

type Stats = {
  hands_won: number;
  hands_lost: number;
  max_balance: number;
  max_bet: number;
  lost_stack: number;
  won_stack: number;
};

type HistoryEntry = {
  game_id: string | null;
  table_id: number;
  user_id: number;
  hole_cards: string[];
  bet: number;
  net_stack_delta: number;
  resulting_balance: number;
  won_hand: boolean;
  board: string[];
  winners: number[];
  pot: number;
};

export default function ProfilePage() {
  const auth = useAuth();
  const toasts = useToasts();
  const [stats, setStats] = useState<Stats | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [loadingStats, setLoadingStats] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const historyLenRef = React.useRef(0);

  const refreshStats = useCallback(async () => {
    setLoadingStats(true);
    try {
      const s = await apiGet<Stats>("/stats/me/stats", auth.token);
      setStats(s);
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : "Не удалось загрузить статистику";
      toasts.push({ title: "Ошибка", message: msg, tone: "bad" });
    } finally {
      setLoadingStats(false);
    }
  }, [auth.token, toasts]);

  const loadMoreHistory = useCallback(
    async (reset?: boolean) => {
      setLoadingHistory(true);
      try {
        const limit = 20;
        const offset = reset ? 0 : historyLenRef.current;
        const items = await apiGet<HistoryEntry[]>(`/stats/me/history?limit=${limit}&offset=${offset}`, auth.token);
        setHistory((prev) => {
          const next = reset ? items : [...prev, ...items];
          historyLenRef.current = next.length;
          return next;
        });
        setHasMore(items.length === limit);
      } catch (e) {
        const msg = e instanceof ApiError ? e.message : "Не удалось загрузить историю";
        toasts.push({ title: "Ошибка", message: msg, tone: "bad" });
      } finally {
        setLoadingHistory(false);
      }
    },
    [auth.token, toasts],
  );

  useEffect(() => {
    void refreshStats();
    void loadMoreHistory(true);
  }, [loadMoreHistory, refreshStats]);

  const winRate = useMemo(() => {
    if (!stats) return null;
    const total = stats.hands_won + stats.hands_lost;
    if (total <= 0) return "—";
    return `${Math.round((stats.hands_won / total) * 100)}%`;
  }, [stats]);

  return (
    <div className="profileGrid">
      <Panel className="profileCard">
        <PanelHeader>
          <div>
            <PanelTitle>Профиль</PanelTitle>
            <PanelSubtitle>Аккаунт и статистика</PanelSubtitle>
          </div>
          <div className="row wrap">
            <Badge className="mono">id: {auth.user?.id}</Badge>
            <Badge className="mono" tone="good">
              {auth.user?.balance ?? 0} фишек
            </Badge>
          </div>
        </PanelHeader>
        <PanelBody>
          <div className="row wrap">
            <Badge tone="good">username: {auth.user?.username}</Badge>
            <Badge>winrate: {winRate ?? "—"}</Badge>
            <div className="spacer" />
            <Button disabled={loadingStats} onClick={() => void refreshStats()}>
              Обновить
            </Button>
          </div>

          <div className="statTiles">
            <div className="tile">
              <div className="tileLabel">Побед</div>
              <div className="tileValue">{stats?.hands_won ?? 0}</div>
            </div>
            <div className="tile">
              <div className="tileLabel">Поражений</div>
              <div className="tileValue">{stats?.hands_lost ?? 0}</div>
            </div>
            <div className="tile">
              <div className="tileLabel">Max bet</div>
              <div className="tileValue mono">{stats?.max_bet ?? 0}</div>
            </div>
            <div className="tile">
              <div className="tileLabel">Max balance</div>
              <div className="tileValue mono">{stats?.max_balance ?? 0}</div>
            </div>
            <div className="tile">
              <div className="tileLabel">Won stack</div>
              <div className="tileValue mono">{stats?.won_stack ?? 0}</div>
            </div>
            <div className="tile">
              <div className="tileLabel">Lost stack</div>
              <div className="tileValue mono">{stats?.lost_stack ?? 0}</div>
            </div>
          </div>
        </PanelBody>
      </Panel>

      <Panel>
        <PanelHeader>
          <div>
            <PanelTitle>История</PanelTitle>
            <PanelSubtitle>Последние раздачи</PanelSubtitle>
          </div>
          <div className="row wrap">
            <Button
              disabled={loadingHistory}
              onClick={() => {
                setHasMore(true);
                void loadMoreHistory(true);
              }}
            >
              Обновить
            </Button>
          </div>
        </PanelHeader>
        <PanelBody>
          {history.length === 0 ? (
            <div className="muted">{loadingHistory ? "Загружаем..." : "Пока нет сыгранных раздач"}</div>
          ) : (
            <div className="historyList">
              {history.map((h, idx) => (
                <div key={`${h.game_id ?? "null"}-${idx}`} className="historyRow">
                  <div className="historyMain">
                    <div className="historyTitle">
                      <span className="mono">Стол #{h.table_id}</span>
                      <span className="dotSep">·</span>
                      <span className={h.won_hand ? "textGood" : "textBad"}>{h.won_hand ? "победа" : "поражение"}</span>
                    </div>
                    <div className="historyMeta">
                      <Badge className="mono">Банк: {h.pot}</Badge>
                      <Badge className="mono">Ставка: {h.bet}</Badge>
                      <Badge className="mono">Итог: {h.net_stack_delta}</Badge>
                      <Badge className="mono">Баланс: {h.resulting_balance}</Badge>
                    </div>
                    <div className="historyCards mono">
                      <span>Карты: {h.hole_cards.join(" ") || "—"}</span>
                      <span className="dotSep">·</span>
                      <span>Стол: {h.board.join(" ") || "—"}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="row wrap">
            <div className="spacer" />
            <Button disabled={!hasMore || loadingHistory} onClick={() => void loadMoreHistory()}>
              Показать ещё
            </Button>
          </div>
        </PanelBody>
      </Panel>
    </div>
  );
}
