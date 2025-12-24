import React, { useMemo } from "react";
import CardView from "@/ui/poker/CardView";
import type { TableState } from "@/ui/poker/types";
import { seatPositions } from "@/ui/poker/seatLayout";
import Badge from "@/ui/kit/Badge";

function statusDotClass(playerStatus: string, isTurn: boolean) {
  if (isTurn) return "dot dotTurn";
  const lowered = (playerStatus || "").toLowerCase();
  if (lowered.includes("fold") || lowered.includes("out")) return "dot dotOut";
  return "dot";
}

export default function TableStage({
  state,
  myId,
  maxPlayers,
  displayName,
}: {
  state: TableState;
  myId: number | null;
  maxPlayers: number;
  displayName: (userId: number) => string;
}) {
  const positions = useMemo(() => seatPositions(Math.max(2, Math.min(9, maxPlayers))), [maxPlayers]);
  const players = state.players.slice().sort((a, b) => a.position - b.position);
  const winners = (state.winners ?? []).filter((x) => typeof x === "number");

  return (
    <div className="tableStage">
      <div className="tableHud">
        <div className="tableCenter">
          <div className="tableHudRow">
            <Badge>Фаза: {state.phase}</Badge>
            {state.current_player_id ? <Badge tone="good">Ходит: {displayName(state.current_player_id)}</Badge> : null}
            {state.current_bet !== null ? <Badge tone="warn">Текущая ставка: {state.current_bet}</Badge> : null}
            {state.phase === "finished" && winners.length ? <Badge tone="good">Победил(и): {winners.map(displayName).join(", ")}</Badge> : null}
          </div>

          <div className="boardRow" aria-label="Board cards">
            {Array.from({ length: 5 }).map((_, idx) => (
              <CardView key={idx} code={state.board[idx] ?? ""} />
            ))}
          </div>
        </div>

        <div className="seatLayer">
          {players.map((p) => {
            const pos = positions[p.position % positions.length];
            const left = `${pos.x}%`;
            const top = `${pos.y}%`;
            const isTurn = state.current_player_id === p.user_id;
            const isMe = myId === p.user_id;
            return (
              <div key={p.user_id} className="seat" style={{ left, top }}>
                <div className={isMe ? "seatBubble seatBubbleMe" : "seatBubble"}>
                  <div className="seatTop">
                    <div className="avatar" />
                    <div>
                      <div className="seatName">
                        {displayName(p.user_id)} {isMe ? "(вы)" : ""}
                      </div>
                      <div className="seatSub">{p.status || "active"}</div>
                    </div>
                    <div className="seatBadges">
                      <div className={statusDotClass(p.status, isTurn)} />
                    </div>
                  </div>

                  {p.hole_cards ? (
                    <div className="holeRow" aria-label="Hole cards">
                      <CardView code={p.hole_cards[0] ?? ""} />
                      <CardView code={p.hole_cards[1] ?? ""} />
                    </div>
                  ) : (
                    <div className="holeRow" aria-label="Hole cards hidden">
                      <div className="cardBack" />
                      <div className="cardBack" />
                    </div>
                  )}

                  <div className="seatBottom mono">
                    <div className="chips">Stack: {p.stack}</div>
                    <div className="bet">Bet: {p.bet}</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
