import { Navigate, Outlet } from "react-router-dom";
import { tokenStorage } from "../lib/auth/tokenStorage";

export function PublicLayout() {
  const token = tokenStorage.get();
  if (token) return <Navigate replace to="/lobby" />;

  return (
    <div className="mx-auto flex min-h-dvh max-w-md flex-col justify-center p-6">
      <div className="rounded-2xl border border-slate-800 bg-slate-900/30 p-6">
        <Outlet />
      </div>
    </div>
  );
}
