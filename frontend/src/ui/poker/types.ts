export type TableSummary = {
  id: string;
  max_players: number;
  buy_in: number;
  private: boolean;
  players_count: number;
  spectators_count: number;
};

export type TableInfo = TableSummary & {
  seats: Array<{
    position: number;
    user_id: number;
    stack: number;
    is_spectator: boolean;
  }>;
};

export type TableStatePlayer = {
  user_id: number;
  position: number;
  stack: number;
  bet: number;
  status: string;
  hole_cards?: string[];
};

export type TableState = {
  table_id: string;
  phase: string;
  hand_active?: boolean;
  pot: number;
  board: string[];
  players: TableStatePlayer[];
  winners?: number[];
  best_hand_rank?: string | null;
  best_hand_cards?: string[];
  current_player_id: number | null;
  current_bet: number | null;
  min_bet: number | null;
};

export type WsEnvelope =
  | { type: "table_state"; payload: TableState }
  | { type: "error"; code?: string; message: string }
  | { type: string; [k: string]: unknown };
