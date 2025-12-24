import React, { useCallback, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import Segmented from "@/ui/components/Segmented";
import { ApiError } from "@/ui/lib/http";
import { useAuth } from "@/ui/auth/AuthContext";
import { useToasts } from "@/ui/toasts/ToastContext";
import { apiBaseUrl } from "@/ui/lib/env";
import Button from "@/ui/kit/Button";
import Input from "@/ui/kit/Input";
import Badge from "@/ui/kit/Badge";
import { Panel, PanelBody, PanelHeader, PanelSubtitle, PanelTitle } from "@/ui/kit/Panel";

type Mode = "login" | "register";

export default function LoginPage() {
  const auth = useAuth();
  const toasts = useToasts();
  const navigate = useNavigate();
  const location = useLocation();

  const [mode, setMode] = useState<Mode>("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const header = useMemo(() => {
    if (mode === "login") return { title: "Вход", sub: "Один шаг до стола." };
    return { title: "Регистрация", sub: "Создайте аккаунт и получите стартовый баланс." };
  }, [mode]);

  const redirectTo = useMemo(() => {
    const raw = (location.state as { from?: string } | null)?.from;
    if (!raw) return "/";
    if (typeof raw !== "string") return "/";
    if (!raw.startsWith("/")) return "/";
    return raw;
  }, [location.state]);

  const submit = useCallback(async () => {
    if (loading) return;
    setLoading(true);
    try {
      if (mode === "login") await auth.login(username.trim(), password);
      else await auth.register(username.trim(), password);
      navigate(redirectTo);
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : "Не удалось выполнить запрос";
      toasts.push({ title: "Ошибка", message: msg, tone: "bad" });
    } finally {
      setLoading(false);
    }
  }, [auth, loading, mode, navigate, password, redirectTo, toasts, username]);

  return (
    <div className="pageGrid">
      <Panel>
        <PanelHeader>
          <div>
            <PanelTitle>{header.title}</PanelTitle>
            <PanelSubtitle>{header.sub}</PanelSubtitle>
          </div>
          <Segmented<Mode>
            value={mode}
            options={[
              { value: "login", label: "Вход" },
              { value: "register", label: "Регистрация" },
            ]}
            onChange={setMode}
          />
        </PanelHeader>
        <PanelBody>
          <form
            className="form"
            onSubmit={(e) => {
              e.preventDefault();
              void submit();
            }}
          >
            <label className="field">
              <div className="fieldLabel">Username</div>
              <Input value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" />
            </label>
            <label className="field">
              <div className="fieldLabel">Password</div>
              <Input
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                type="password"
                autoComplete={mode === "login" ? "current-password" : "new-password"}
              />
            </label>

            <div className="row wrap">
              <Button
                variant="primary"
                type="submit"
                disabled={loading || username.trim().length < 2 || password.length < 3}
                onClick={() => void submit()}
              >
                {mode === "login" ? "Войти" : "Создать аккаунт"}
              </Button>

              <div className="spacer" />
              {auth.status === "authed" ? <Badge tone="good">Вы уже вошли</Badge> : null}
            </div>

            <div className="hint">
              API: <span className="mono">{apiBaseUrl()}</span>
            </div>
          </form>
        </PanelBody>
      </Panel>

      <Panel>
        <PanelHeader>
          <PanelTitle>Как это работает</PanelTitle>
          <Badge>REST + WebSocket</Badge>
        </PanelHeader>
        <PanelBody>
          <div className="steps">
            <div className="step">
              <div className="stepNum">1</div>
              <div>
                <div className="stepTitle">Войдите</div>
                <div className="stepText">Сессия хранится в браузере, можно перезагружать страницу.</div>
              </div>
            </div>
            <div className="step">
              <div className="stepNum">2</div>
              <div>
                <div className="stepTitle">Выберите стол</div>
                <div className="stepText">В лобби видны публичные столы и их заполненность.</div>
              </div>
            </div>
            <div className="step">
              <div className="stepNum">3</div>
              <div>
                <div className="stepTitle">Сядьте игроком или смотрите</div>
                <div className="stepText">Игрок делает buy-in, зритель может включить показ карт.</div>
              </div>
            </div>
            <div className="step">
              <div className="stepNum">4</div>
              <div>
                <div className="stepTitle">Играйте</div>
                <div className="stepText">Ходы идут через WebSocket, состояние обновляется мгновенно.</div>
              </div>
            </div>
          </div>
        </PanelBody>
      </Panel>
    </div>
  );
}
