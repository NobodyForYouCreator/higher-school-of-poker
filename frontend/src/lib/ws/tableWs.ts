import type { WsClientMessage, WsServerMessage } from "../../types/ws";
import { env } from "../env";

function joinUrl(baseUrl: string, path: string) {
  const normalizedBaseUrl = baseUrl.endsWith("/")
    ? baseUrl.slice(0, -1)
    : baseUrl;
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${normalizedBaseUrl}${normalizedPath}`;
}

export function connectTableWs(tableId: string, token: string) {
  const url = new URL(joinUrl(env.wsBaseUrl, `/ws/tables/${tableId}`));
  url.searchParams.set("token", token);

  const socket = new WebSocket(url);

  return {
    socket,
    send(message: WsClientMessage) {
      socket.send(JSON.stringify(message));
    },
    onMessage(handler: (message: WsServerMessage) => void) {
      socket.addEventListener("message", (event) => {
        try {
          handler(JSON.parse(String(event.data)) as WsServerMessage);
        } catch {
          // ignore
        }
      });
    }
  };
}

