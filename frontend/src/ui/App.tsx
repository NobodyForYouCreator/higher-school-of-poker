import React, { useMemo } from "react";
import { NavLink, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import LobbyPage from "@/ui/pages/LobbyPage";
import LoginPage from "@/ui/pages/LoginPage";
import ProfilePage from "@/ui/pages/ProfilePage";
import TablePage from "@/ui/pages/TablePage";
import { AuthProvider, useAuth } from "@/ui/auth/AuthContext";
import { ToastProvider, useToasts } from "@/ui/toasts/ToastContext";

function Shell() {
  const auth = useAuth();
  const toasts = useToasts();
  const location = useLocation();
  const navigate = useNavigate();

  const pills = useMemo(() => {
    const isActive = (path: string) => location.pathname === path || location.pathname.startsWith(path + "/");
    return [
      { to: "/", label: "Лобби", active: isActive("/") },
      { to: "/profile", label: "Профиль", active: isActive("/profile") },
    ];
  }, [location.pathname]);

  return (
    <div className="appShell">
      <div className="topbar">
        <div className="topbarInner">
          <div className="brand">
            <div className="logo" />
            <div>
              <div className="brandTitle">Higher School of Poker</div>
              <div className="brandSub">Лобби · столы · раздачи в реальном времени</div>
            </div>
          </div>

          <div className="nav">
            {auth.status === "authed" ? (
              <>
                {pills.map((p) => (
                  <NavLink key={p.to} to={p.to} className={() => (p.active ? "pill pillActive" : "pill")}>
                    {p.label}
                  </NavLink>
                ))}
                <span className="badge">Вы: {auth.user?.username ?? "—"}</span>
                <button
                  className="btn btnGhost"
                  onClick={() => {
                    auth.logout();
                    toasts.push({ title: "Вы вышли", message: "Токен удалён." });
                    navigate("/login");
                  }}
                >
                  Выйти
                </button>
              </>
            ) : (
              <NavLink to="/login" className="pill pillActive">
                Войти
              </NavLink>
            )}
          </div>
        </div>
      </div>

      <div className="content">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<LobbyPage />} />
          <Route path="/tables/:tableId" element={<TablePage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="*" element={<LobbyPage />} />
        </Routes>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <Shell />
      </AuthProvider>
    </ToastProvider>
  );
}
