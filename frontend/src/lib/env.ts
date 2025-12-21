function trimTrailingSlash(value: string) {
  return value.replace(/\/+$/, "");
}

function ensureApiPrefix(baseUrl: string) {
  const normalized = trimTrailingSlash(baseUrl);
  return normalized.endsWith("/api") ? normalized : `${normalized}/api`;
}

function deriveWsBaseUrl(apiBaseUrl: string) {
  if (apiBaseUrl.startsWith("https://")) return apiBaseUrl.replace("https://", "wss://");
  if (apiBaseUrl.startsWith("http://")) return apiBaseUrl.replace("http://", "ws://");
  return "ws://localhost:8000";
}

const rawApiBaseUrl = trimTrailingSlash(import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000");

export const env = {
  apiBaseUrl: ensureApiPrefix(rawApiBaseUrl),
  wsBaseUrl: trimTrailingSlash(
    import.meta.env.VITE_WS_BASE_URL ??
      deriveWsBaseUrl(rawApiBaseUrl)
  )
};
