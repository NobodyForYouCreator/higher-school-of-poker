import React, { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "@/ui/auth/AuthContext";
import Spinner from "@/ui/kit/Spinner";

export default function RequireAuth({ children }: { children: React.ReactNode }) {
  const auth = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (auth.status === "guest") {
      navigate("/login", { replace: true, state: { from: location.pathname } });
    }
  }, [auth.status, location.pathname, navigate]);

  if (auth.status === "loading") {
    return (
      <div className="center">
        <Spinner size={22} />
        <div className="muted">Проверяем сессию...</div>
      </div>
    );
  }
  if (auth.status !== "authed") return null;
  return <>{children}</>;
}
