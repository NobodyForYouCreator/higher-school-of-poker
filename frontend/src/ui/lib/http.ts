import { apiBaseUrl } from "@/ui/lib/env";

export class ApiError extends Error {
  status: number;
  bodyText: string;
  constructor(message: string, status: number, bodyText: string) {
    super(message);
    this.status = status;
    this.bodyText = bodyText;
  }
}

function urlFor(path: string) {
  const base = apiBaseUrl().replace(/\/$/, "");
  const p = path.startsWith("/") ? path : `/${path}`;
  if (base.endsWith("/api")) return `${base}${p}`;
  return `${base}/api${p}`;
}

async function parseJsonOrText(res: Response) {
  const contentType = res.headers.get("content-type") ?? "";
  const text = await res.text();
  if (!text) return null;
  if (contentType.includes("application/json")) {
    try {
      return JSON.parse(text);
    } catch {
      return text;
    }
  }
  return text;
}

export async function apiGet<T>(path: string, token?: string | null): Promise<T> {
  const res = await fetch(urlFor(path), {
    method: "GET",
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  });
  const payload = await parseJsonOrText(res);
  if (!res.ok) {
    const detail = typeof payload === "string" ? null : (payload as any)?.detail;
    const msg =
      typeof payload === "string"
        ? payload
        : typeof detail === "string"
          ? detail
          : typeof detail?.message === "string"
            ? detail.message
            : "Request failed";
    throw new ApiError(msg, res.status, typeof payload === "string" ? payload : JSON.stringify(payload));
  }
  return payload as T;
}

export async function apiPost<TOut, TIn extends Record<string, unknown>>(
  path: string,
  body: TIn,
  token?: string | null,
): Promise<TOut> {
  const res = await fetch(urlFor(path), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(body),
  });
  const payload = await parseJsonOrText(res);
  if (!res.ok) {
    const detail = typeof payload === "string" ? null : (payload as any)?.detail;
    const msg =
      typeof payload === "string"
        ? payload
        : typeof detail === "string"
          ? detail
          : typeof detail?.message === "string"
            ? detail.message
            : "Request failed";
    throw new ApiError(msg, res.status, typeof payload === "string" ? payload : JSON.stringify(payload));
  }
  return payload as TOut;
}

export async function apiPostEmpty<TOut>(path: string, token?: string | null): Promise<TOut> {
  const res = await fetch(urlFor(path), {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  });
  const payload = await parseJsonOrText(res);
  if (!res.ok) {
    const detail = typeof payload === "string" ? null : (payload as any)?.detail;
    const msg =
      typeof payload === "string"
        ? payload
        : typeof detail === "string"
          ? detail
          : typeof detail?.message === "string"
            ? detail.message
            : "Request failed";
    throw new ApiError(msg, res.status, typeof payload === "string" ? payload : JSON.stringify(payload));
  }
  return payload as TOut;
}
