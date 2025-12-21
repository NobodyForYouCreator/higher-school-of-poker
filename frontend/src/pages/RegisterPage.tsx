import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authApi } from "../lib/api/auth";
import { ApiError } from "../lib/api/client";
import { tokenStorage } from "../lib/auth/tokenStorage";

export function RegisterPage() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  return (
    <div className="flex flex-col gap-4">
      <div>
        <h1 className="text-2xl font-semibold">Регистрация</h1>
        <p className="mt-1 text-sm text-slate-400">Создание аккаунта.</p>
      </div>

      <form
        className="flex flex-col gap-3"
        onSubmit={async (event) => {
          event.preventDefault();
          setError(null);
          setIsSubmitting(true);

          try {
            const { access_token } = await authApi.register({
              username: username.trim(),
              password
            });
            tokenStorage.set(access_token);
            navigate("/lobby", { replace: true });
          } catch (err) {
            if (err instanceof ApiError) {
              setError("Не удалось зарегистрироваться. Проверь данные и доступность API.");
            } else {
              setError("Не удалось зарегистрироваться.");
            }
          } finally {
            setIsSubmitting(false);
          }
        }}
      >
        <label className="flex flex-col gap-1">
          <span className="text-sm text-slate-300">Логин</span>
          <input
            className="rounded-xl border border-slate-800 bg-slate-950/40 px-3 py-2 outline-none focus:border-slate-600"
            name="username"
            placeholder="nikita"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </label>

        <label className="flex flex-col gap-1">
          <span className="text-sm text-slate-300">Пароль</span>
          <input
            className="rounded-xl border border-slate-800 bg-slate-950/40 px-3 py-2 outline-none focus:border-slate-600"
            name="password"
            placeholder="••••••••"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>

        <button
          className="mt-2 rounded-xl bg-emerald-500 px-4 py-2 font-medium text-emerald-950 hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60"
          disabled={
            isSubmitting ||
            username.trim().length === 0 ||
            password.length === 0
          }
          type="submit"
        >
          {isSubmitting ? "Создаём..." : "Создать аккаунт"}
        </button>
      </form>

      {error ? (
        <div className="rounded-xl border border-red-900/60 bg-red-950/30 p-3 text-sm text-red-200">
          {error}
        </div>
      ) : null}

      {import.meta.env.DEV ? (
        <button
          className="rounded-xl border border-slate-700 bg-slate-950/20 px-4 py-2 text-sm text-slate-200 hover:bg-slate-900"
          onClick={() => {
            tokenStorage.set("dev-token");
            navigate("/lobby", { replace: true });
          }}
          type="button"
        >
          Dev: создать токен и зайти
        </button>
      ) : null}

      <div className="text-sm text-slate-400">
        Уже есть аккаунт?{" "}
        <Link className="text-emerald-300 hover:text-emerald-200" to="/login">
          Войти
        </Link>
      </div>
    </div>
  );
}
