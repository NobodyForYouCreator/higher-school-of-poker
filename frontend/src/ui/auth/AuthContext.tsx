import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { apiGet, apiPost, ApiError } from "@/ui/lib/http";
import { tokenStorage } from "@/ui/lib/tokenStorage";
import { useToasts } from "@/ui/toasts/ToastContext";

type AuthStatus = "loading" | "guest" | "authed";

export type Me = {
  id: number;
  username: string;
};

type RegisterResponse = {
  access_token: string;
  token_type: string;
};

type AuthContextValue = {
  status: AuthStatus;
  token: string | null;
  user: Me | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshMe: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const toasts = useToasts();
  const [status, setStatus] = useState<AuthStatus>("loading");
  const [token, setToken] = useState<string | null>(tokenStorage.get());
  const [user, setUser] = useState<Me | null>(null);

  const logout = useCallback(() => {
    tokenStorage.clear();
    setToken(null);
    setUser(null);
    setStatus("guest");
  }, []);

  const refreshMe = useCallback(async () => {
    const t = tokenStorage.get();
    setToken(t);
    if (!t) {
      setStatus("guest");
      setUser(null);
      return;
    }

    try {
      const me = await apiGet<Me>("/auth/me", t);
      setUser(me);
      setStatus("authed");
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        logout();
        return;
      }
      setStatus("guest");
      setUser(null);
    }
  }, [logout]);

  useEffect(() => {
    void refreshMe();
  }, [refreshMe]);

  const login = useCallback(
    async (username: string, password: string) => {
      const res = await apiPost<RegisterResponse, { username: string; password: string }>("/auth/login", {
        username,
        password,
      });
      tokenStorage.set(res.access_token);
      setToken(res.access_token);
      await refreshMe();
      toasts.push({ title: "Успешный вход", message: `Добро пожаловать, ${username}.` });
    },
    [refreshMe, toasts],
  );

  const register = useCallback(
    async (username: string, password: string) => {
      const res = await apiPost<RegisterResponse, { username: string; password: string }>("/auth/register", {
        username,
        password,
      });
      tokenStorage.set(res.access_token);
      setToken(res.access_token);
      await refreshMe();
      toasts.push({ title: "Аккаунт создан", message: `Добро пожаловать, ${username}.` });
    },
    [refreshMe, toasts],
  );

  const value = useMemo<AuthContextValue>(
    () => ({ status, token, user, login, register, logout, refreshMe }),
    [status, token, user, login, register, logout, refreshMe],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

