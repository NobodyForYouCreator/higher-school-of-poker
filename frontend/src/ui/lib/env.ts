export function apiBaseUrl() {
  const explicit = import.meta.env.VITE_API_URL as string | undefined;
  if (explicit) return explicit;
  if (import.meta.env.DEV) return "http://localhost:8000";
  return window.location.origin;
}

export function wsBaseUrl() {
  const explicit = import.meta.env.VITE_WS_URL as string | undefined;
  if (explicit) return explicit;

  let api = apiBaseUrl();
  api = api.replace(/\/$/, "");
  if (api.endsWith("/api")) api = api.slice(0, -4);
  if (api.startsWith("https://")) return api.replace("https://", "wss://");
  if (api.startsWith("http://")) return api.replace("http://", "ws://");
  return "ws://localhost:8000";
}
