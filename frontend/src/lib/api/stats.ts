import type { HandHistoryItem, PlayerStats } from "../../types/api";
import { apiGet } from "./client";

export const statsApi = {
  myStats() {
    return apiGet<PlayerStats>("/stats/me/stats");
  },
  myHistory() {
    return apiGet<HandHistoryItem[]>("/stats/me/history");
  }
};

