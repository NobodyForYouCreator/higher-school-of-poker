export function apiBaseUrl() {
  return (import.meta.env.VITE_API_URL as string | undefined) ?? "http://localhost:20001";
}

export function wsBaseUrl() {
  const explicit = import.meta.env.VITE_WS_URL as string | undefined;
  if (explicit) return explicit;

  let api = apiBaseUrl();
  api = api.replace(/\/$/, "");
  if (api.endsWith("/api")) api = api.slice(0, -4);
  if (api.startsWith("https://")) return api.replace("https://", "wss://");
  if (api.startsWith("http://")) return api.replace("http://", "ws://");
  return "ws://localhost:20001";
}
