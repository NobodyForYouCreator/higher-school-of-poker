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
        <div className="cardCorner cardCornerRankTopLeft">
          <span className="cardRank">{rank}</span>
        </div>
        <div className="cardCorner cardCornerSuitTopRight">
          <span className="cardSuit">{suit}</span>
        </div>
        <div className="cardPip">{suit}</div>
        <div className="cardCorner cardCornerSuitBottomLeft">
          <span className="cardSuit">{suit}</span>
        </div>
        <div className="cardCorner cardCornerRankBottomRight">
          <span className="cardRank">{rank}</span>
        </div>
      </div>
    </div>
  );
}
