import { useEffect } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { tokenStorage } from "./lib/auth/tokenStorage";

function navLinkClassName({ isActive }: { isActive: boolean }) {
  return [
    "rounded-lg px-3 py-2 text-sm transition",
    isActive ? "bg-slate-800 text-slate-50" : "text-slate-300 hover:bg-slate-900"
  ].join(" ");
}

export function AppShell() {
  const navigate = useNavigate();

  useEffect(() => {
    function onAuthChanged() {
      const token = tokenStorage.get();
      if (!token) {
        navigate("/login", { replace: true });
      }
    }

    window.addEventListener("hsepoker:auth", onAuthChanged);
    return () => window.removeEventListener("hsepoker:auth", onAuthChanged);
  }, [navigate]);

  return (
    <div className="mx-auto flex min-h-dvh max-w-6xl flex-col gap-6 p-6">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="text-lg font-semibold">HSE Poker</div>
          <span className="rounded-full border border-slate-800 bg-slate-900/50 px-2 py-1 text-xs text-slate-400">
            alpha
          </span>
        </div>

        <nav className="flex items-center gap-2">
          <NavLink className={navLinkClassName} to="/lobby">
            Лобби
          </NavLink>
          <NavLink className={navLinkClassName} to="/profile">
            Профиль
          </NavLink>
          <button
            className="rounded-lg px-3 py-2 text-sm text-slate-300 transition hover:bg-slate-900"
            onClick={() => {
              tokenStorage.clear();
              navigate("/login", { replace: true });
            }}
            type="button"
          >
            Выйти
          </button>
        </nav>
      </header>

      <main className="flex-1 rounded-2xl border border-slate-800 bg-slate-900/30 p-6">
        <Outlet />
      </main>
    </div>
  );
}
