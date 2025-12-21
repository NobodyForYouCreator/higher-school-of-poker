export type JwtTokenResponse = {
  access_token: string;
  token_type?: "bearer" | string;
};

export type User = {
  id: number;
  username: string;
  email?: string;
  balance?: number;
  created_at?: string;
};

export type TableSummary = {
  id: string;
  max_players: number;
  buy_in: number;
  private: boolean;
  players_count?: number;
  spectators_count?: number;
};

export type TableCreateRequest = {
  max_players: number;
  buy_in: number;
  private: boolean;
};

export type TableInfo = TableSummary & {
  seats?: Array<{
    position: number;
    user_id?: number;
    username?: string;
    stack?: number;
    is_spectator?: boolean;
  }>;
};

export type PlayerStats = {
  hands_won: number;
  hands_lost: number;
  max_balance?: number;
  max_bet?: number;
  lost_stack?: number;
  won_stack?: number;
};

export type HandHistoryItem = {
  id: string;
  table_id?: string;
  finished_at?: string;
  result?: "win" | "loss" | "split" | string;
  pot?: number;
};
