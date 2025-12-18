import type { PropsWithChildren } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { tokenStorage } from "../lib/auth/tokenStorage";

export function RequireAuth({ children }: PropsWithChildren) {
  const location = useLocation();
  const token = tokenStorage.get();

  if (!token) {
    return <Navigate replace state={{ from: location }} to="/login" />;
  }

  return children;
}

