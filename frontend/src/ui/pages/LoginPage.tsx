import React, { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import Segmented from "@/ui/components/Segmented";
import { ApiError } from "@/ui/lib/http";
import { useAuth } from "@/ui/auth/AuthContext";
import { useToasts } from "@/ui/toasts/ToastContext";

type Mode = "login" | "register";

export default function LoginPage() {
  const auth = useAuth();
  const toasts = useToasts();
  const navigate = useNavigate();

  const [mode, setMode] = useState<Mode>("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const header = useMemo(() => {
    if (mode === "login") return { title: "Вход", sub: "Вернём вас за стол за пару секунд." };
    return { title: "Регистрация", sub: "Создайте аккаунт и начните игру." };
  }, [mode]);

  return (
    <div className="grid2">
      <div className="panel">
        <div className="panelHeader">
          <div>
            <div className="panelTitle">{header.title}</div>
            <div className="hint">{header.sub}</div>
          </div>
          <Segmented<Mode>
            value={mode}
            options={[
              { value: "login", label: "Вход" },
              { value: "register", label: "Регистрация" },
            ]}
            onChange={setMode}
          />
        </div>
        <div className="panelBody">
          <div style={{ display: "grid", gap: 12 }}>
            <label>
              <div className="hint">Username</div>
              <input className="input" value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" />
            </label>
            <label>
              <div className="hint">Password</div>
              <input
                className="input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                type="password"
                autoComplete={mode === "login" ? "current-password" : "new-password"}
              />
            </label>

            <div className="row">
              <button
                className="btn btnPrimary"
                disabled={loading || username.trim().length < 2 || password.length < 3}
                onClick={async () => {
                  setLoading(true);
                  try {
                    if (mode === "login") await auth.login(username.trim(), password);
                    else await auth.register(username.trim(), password);
                    navigate("/");
                  } catch (e) {
                    const msg = e instanceof ApiError ? e.message : "Не удалось выполнить запрос";
                    toasts.push({ title: "Ошибка", message: msg, tone: "bad" });
                  } finally {
                    setLoading(false);
                  }
                }}
              >
                {loading ? "..." : mode === "login" ? "Войти" : "Создать аккаунт"}
              </button>

              <div className="spacer" />
              {auth.status === "authed" ? <span className="badge badgeGood">Вы уже вошли</span> : null}
            </div>

            <div className="hint">
              API по умолчанию: <span className="mono">http://localhost:8000</span> (можно изменить через{" "}
              <span className="mono">VITE_API_URL</span>).
            </div>
          </div>
        </div>
      </div>

      <div className="panel">
        <div className="panelHeader">
          <div className="panelTitle">Как играть</div>
          <span className="badge">WS + REST</span>
        </div>
        <div className="panelBody">
          <div className="muted" style={{ lineHeight: 1.6 }}>
            <div>1) Войдите / зарегистрируйтесь</div>
            <div>2) В лобби выберите стол или создайте новый</div>
            <div>3) На странице стола — сядьте игроком или зайдите зрителем</div>
            <div>4) Ходы идут через WebSocket, состояние обновляется мгновенно</div>
          </div>
        </div>
      </div>
    </div>
  );
}

