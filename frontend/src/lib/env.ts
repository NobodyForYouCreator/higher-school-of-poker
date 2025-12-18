function trimTrailingSlash(value: string) {
  return value.replace(/\/+$/, "");
}

function deriveWsBaseUrl(apiBaseUrl: string) {
  if (apiBaseUrl.startsWith("https://")) return apiBaseUrl.replace("https://", "wss://");
  if (apiBaseUrl.startsWith("http://")) return apiBaseUrl.replace("http://", "ws://");
  return "ws://localhost:8000";
}

export const env = {
  apiBaseUrl: trimTrailingSlash(
    import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"
  ),
  wsBaseUrl: trimTrailingSlash(
    import.meta.env.VITE_WS_BASE_URL ??
      deriveWsBaseUrl(import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000")
  )
};

