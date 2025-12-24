import React from "react";
import { isRedSuit, parseCard, rankLabel, suitSymbol } from "@/ui/poker/cards";

export default function CardView({ code }: { code: string }) {
  const parsed = parseCard(code);
  if (!parsed) return <div className="cardBack" aria-label="card back" />;
  const colorClass = isRedSuit(parsed.suit) ? "cardRed" : "cardBlack";
  const rank = rankLabel(parsed.rank);
  const suit = suitSymbol(parsed.suit);

  return (
    <div className={`card ${colorClass}`} aria-label={`${rank}${suit}`}>
      <div className="cardInner">
        <div className="cardTop">
          <div className="cardRank">{rank}</div>
          <div className="cardSuit">{suit}</div>
        </div>
        <div className="cardPip">{suit}</div>
      </div>
    </div>
  );
}
