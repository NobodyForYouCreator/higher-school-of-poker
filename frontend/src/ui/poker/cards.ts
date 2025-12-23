export type Suit = "H" | "D" | "C" | "S";
export type Rank = "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" | "T" | "J" | "Q" | "K" | "A";

export type CardCode = `${Rank}${Suit}`;

const SUIT_SYMBOL: Record<Suit, string> = {
  H: "♥",
  D: "♦",
  C: "♣",
  S: "♠",
};

export function suitSymbol(suit: Suit) {
  return SUIT_SYMBOL[suit];
}

export function isRedSuit(suit: Suit) {
  return suit === "H" || suit === "D";
}

export function parseCard(code: string): { rank: Rank; suit: Suit } | null {
  if (typeof code !== "string" || code.length < 2) return null;
  const rank = code[0] as Rank;
  const suit = code[1] as Suit;
  const validRank = "23456789TJQKA".includes(rank);
  const validSuit = "HDCS".includes(suit);
  if (!validRank || !validSuit) return null;
  return { rank, suit };
}

export function rankLabel(rank: Rank) {
  if (rank === "T") return "10";
  return rank;
}

