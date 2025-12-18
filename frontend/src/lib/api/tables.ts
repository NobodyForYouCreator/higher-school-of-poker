import type { TableCreateRequest, TableInfo, TableSummary } from "../../types/api";
import { apiGet, apiPost } from "./client";

export const tablesApi = {
  list() {
    return apiGet<TableSummary[]>("/tables");
  },
  create(payload: TableCreateRequest) {
    return apiPost<TableInfo>("/tables/create", payload);
  },
  get(tableId: string) {
    return apiGet<TableInfo>(`/tables/${tableId}`);
  },
  join(tableId: string) {
    return apiPost<void>(`/tables/${tableId}/join`);
  },
  leave(tableId: string) {
    return apiPost<void>(`/tables/${tableId}/leave`);
  },
  spectate(tableId: string) {
    return apiPost<void>(`/tables/${tableId}/spectate`);
  }
};

