import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="mx-auto flex min-h-dvh max-w-xl flex-col justify-center gap-4 p-6 text-center">
      <h1 className="text-3xl font-semibold">404</h1>
      <p className="text-slate-400">Страница не найдена.</p>
      <div>
        <Link className="text-emerald-300 hover:text-emerald-200" to="/lobby">
          Вернуться в лобби
        </Link>
      </div>
    </div>
  );
}
