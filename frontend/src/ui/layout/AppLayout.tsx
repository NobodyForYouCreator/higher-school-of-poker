import React, { useMemo } from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "@/ui/auth/AuthContext";
import { useToasts } from "@/ui/toasts/ToastContext";
import Badge from "@/ui/kit/Badge";
import Button from "@/ui/kit/Button";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const auth = useAuth();
  const toasts = useToasts();
  const location = useLocation();
  const navigate = useNavigate();

  const navItems = useMemo(() => {
    const isActive = (path: string) => location.pathname === path || location.pathname.startsWith(path + "/");
    return [
      { to: "/", label: "Лобби", active: isActive("/") },
      { to: "/profile", label: "Профиль", active: isActive("/profile") },
    ];
  }, [location.pathname]);

  return (
    <div className="appShell">
      <header className="topbar">
        <div className="topbarInner">
          <div className="brand" role="banner" onClick={() => navigate("/")}>
            <img className="logo" src="/smth.png" alt="" />
            <div>
              <div className="brandTitle">Higher School of Poker</div>
              <div className="brandSub">Лобби · столы · раздачи в реальном времени</div>
            </div>
          </div>

          <nav className="nav" aria-label="Навигация">
            {auth.status === "authed" ? (
              <>
                {navItems.map((p) => (
                  <NavLink key={p.to} to={p.to} className={() => (p.active ? "pill pillActive" : "pill")}>
                    {p.label}
                  </NavLink>
                ))}
                <Badge className="mono" tone="neutral">
                  {auth.user?.username ?? "—"}
                </Badge>
                <Badge className="mono" tone="good">
                  {auth.user?.balance ?? 0} фишек
                </Badge>
                <Button
                  variant="ghost"
                  onClick={() => {
                    auth.logout();
                    toasts.push({ title: "Вы вышли", message: "Сессия завершена." });
                    navigate("/login");
                  }}
                >
                  Выйти
                </Button>
              </>
            ) : (
              <NavLink to="/login" className="pill pillActive">
                Войти
              </NavLink>
            )}
          </nav>
        </div>
      </header>

      <main className="content">{children}</main>
    </div>
  );
}
