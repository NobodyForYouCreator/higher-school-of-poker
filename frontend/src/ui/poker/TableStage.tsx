import React, { useMemo } from "react";
import CardView from "@/ui/poker/CardView";
import type { TableState } from "@/ui/poker/types";
import { seatPositions } from "@/ui/poker/seatLayout";

function statusDotClass(playerStatus: string, isTurn: boolean) {
  if (isTurn) return "dot dotTurn";
  const lowered = (playerStatus || "").toLowerCase();
  if (lowered.includes("fold") || lowered.includes("out")) return "dot dotOut";
  return "dot";
}

function shortId(id: number) {
  return `#${id}`;
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
          <div className="row" style={{ gap: 10, flexWrap: "wrap" }}>
            <span className="badge">Фаза: {state.phase}</span>
            {state.current_player_id ? (
              <span className="badge badgeGood">Ходит: {displayName(state.current_player_id)}</span>
            ) : null}
            {state.current_bet !== null ? <span className="badge badgeWarn">Текущая ставка: {state.current_bet}</span> : null}
            <span className="badge badgeWarn mono">Пот: {state.pot}</span>
            {state.phase === "finished" && winners.length ? (
              <span className="badge badgeGood">Победил(и): {winners.map(displayName).join(", ")}</span>
            ) : null}
          </div>

          <div className="boardRow" aria-label="Board cards">
            {Array.from({ length: 5 }).map((_, idx) => (
              <CardView key={idx} code={state.board[idx] ?? ""} />
            ))}
          </div>
          <div className="potPill mono">Пот: {state.pot}</div>
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
                <div className="seatBubble" style={isMe ? { borderColor: "rgba(124,92,255,.55)" } : undefined}>
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
