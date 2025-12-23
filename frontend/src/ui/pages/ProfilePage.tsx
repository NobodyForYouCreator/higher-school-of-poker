import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/ui/auth/AuthContext";
import { ApiError, apiGet } from "@/ui/lib/http";
import { useToasts } from "@/ui/toasts/ToastContext";

type Stats = {
  hands_won: number;
  hands_lost: number;
  max_balance: number;
  max_bet: number;
  lost_stack: number;
  won_stack: number;
};

export default function ProfilePage() {
  const auth = useAuth();
  const toasts = useToasts();
  const navigate = useNavigate();

  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(false);

  const isAuthed = auth.status === "authed";

  useEffect(() => {
    if (!isAuthed) return;
    setLoading(true);
    apiGet<Stats>("/stats/me/stats", auth.token)
      .then((s) => setStats(s))
      .catch((e) => {
        const msg = e instanceof ApiError ? e.message : "Не удалось загрузить статистику";
        toasts.push({ title: "Ошибка", message: msg, tone: "bad" });
      })
      .finally(() => setLoading(false));
  }, [auth.token, isAuthed, toasts]);

  const winRate = useMemo(() => {
    if (!stats) return null;
    const total = stats.hands_won + stats.hands_lost;
    if (total <= 0) return "—";
    return `${Math.round((stats.hands_won / total) * 100)}%`;
  }, [stats]);

  if (!isAuthed) {
    return (
      <div className="panel">
        <div className="panelHeader">
          <div className="panelTitle">Профиль</div>
        </div>
        <div className="panelBody">
          <div className="muted">
            Нужно войти.{" "}
            <button className="btn btnPrimary" onClick={() => navigate("/login")}>
              Войти
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="grid2">
      <div className="panel">
        <div className="panelHeader">
          <div>
            <div className="panelTitle">Профиль</div>
            <div className="hint">Аккаунт и статистика</div>
          </div>
          <span className="badge">id: {auth.user?.id}</span>
        </div>
        <div className="panelBody">
          <div className="row" style={{ flexWrap: "wrap" }}>
            <span className="badge badgeGood">username: {auth.user?.username}</span>
            <span className="badge">winrate: {winRate ?? "—"}</span>
          </div>
          <div style={{ height: 12 }} />
          <div className="hint">Эндпоинты статистики сейчас возвращают заглушку — UI готов.</div>
        </div>
      </div>

      <div className="panel">
        <div className="panelHeader">
          <div className="panelTitle">Показатели</div>
          <span className="badge">{loading ? "loading" : "ok"}</span>
        </div>
        <div className="panelBody">
          {!stats ? (
            <div className="muted">{loading ? "Загружаем..." : "Нет данных"}</div>
          ) : (
            <div style={{ display: "grid", gap: 10 }}>
              <div className="row">
                <span className="badge">Побед: {stats.hands_won}</span>
                <span className="badge">Поражений: {stats.hands_lost}</span>
              </div>
              <div className="row">
                <span className="badge">Max balance: {stats.max_balance}</span>
                <span className="badge">Max bet: {stats.max_bet}</span>
              </div>
              <div className="row">
                <span className="badge">Won stack: {stats.won_stack}</span>
                <span className="badge">Lost stack: {stats.lost_stack}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

