export type PlayerActionType = "fold" | "check" | "call" | "bet" | "raise";

export type WsClientMessage =
  | {
      type: "player_action";
      payload: { action: PlayerActionType; amount?: number };
    }
  | {
      type: "toggle_show_all";
      payload: { show: boolean };
    };

export type TablePhase = "preflop" | "flop" | "turn" | "river" | "showdown";

export type TableState = {
  table_id: string;
  phase: TablePhase;
  pot: number;
  board: string[];
  players: Array<{
    user_id: number;
    position: number;
    stack: number;
    bet: number;
    status: string;
    hole_cards?: string[];
  }>;
  current_player_id?: number;
  current_bet?: number;
  min_bet?: number;
};

export type WsServerMessage =
  | { type: "table_state"; payload: TableState }
  | { type: "error"; message: string }
  | { type: "info"; message: string };

