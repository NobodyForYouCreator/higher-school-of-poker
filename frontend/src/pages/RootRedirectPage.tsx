import { Navigate } from "react-router-dom";
import { tokenStorage } from "../lib/auth/tokenStorage";

export function RootRedirectPage() {
  const token = tokenStorage.get();
  return <Navigate replace to={token ? "/lobby" : "/login"} />;
}

