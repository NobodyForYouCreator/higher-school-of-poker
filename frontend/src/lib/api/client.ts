import { tokenStorage } from "../auth/tokenStorage";
import { env } from "../env";

export class ApiError extends Error {
  status: number;
  body: unknown;

  constructor(message: string, status: number, body: unknown) {
    super(message);
    this.status = status;
    this.body = body;
  }
}

function joinUrl(baseUrl: string, path: string) {
  const normalizedBaseUrl = baseUrl.endsWith("/")
    ? baseUrl.slice(0, -1)
    : baseUrl;
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${normalizedBaseUrl}${normalizedPath}`;
}

async function parseJsonSafe(response: Response) {
  const text = await response.text();
  if (!text) return undefined;
  try {
    return JSON.parse(text) as unknown;
  } catch {
    return text;
  }
}

type ApiRequestInit = Omit<RequestInit, "body"> & {
  auth?: boolean;
  json?: unknown;
};

export async function apiRequest<T>(
  path: string,
  { auth = true, headers, json, ...init }: ApiRequestInit = {}
): Promise<T> {
  const token = auth ? tokenStorage.get() : null;

  const response = await fetch(joinUrl(env.apiBaseUrl, path), {
    ...init,
    headers: {
      ...(json ? { "Content-Type": "application/json" } : null),
      ...(token ? { Authorization: `Bearer ${token}` } : null),
      ...headers
    },
    body: json ? JSON.stringify(json) : undefined
  });

  const body = await parseJsonSafe(response);

  if (response.status === 401) {
    tokenStorage.clear();
  }

  if (!response.ok) {
    throw new ApiError(`HTTP ${response.status}`, response.status, body);
  }

  return body as T;
}

export function apiGet<T>(path: string, init?: ApiRequestInit) {
  return apiRequest<T>(path, { ...init, method: "GET" });
}

export function apiPost<T>(path: string, json?: unknown, init?: ApiRequestInit) {
  return apiRequest<T>(path, { ...init, method: "POST", json });
}

