export function seatPositions(max: number) {
  const n = Math.max(2, Math.min(9, Math.floor(max)));
  if (n === 2) return [{ x: 34, y: 78 }, { x: 66, y: 78 }];
  if (n === 3) return [{ x: 50, y: 86 }, { x: 26, y: 30 }, { x: 74, y: 30 }];
  if (n === 4) return [{ x: 25, y: 74 }, { x: 75, y: 74 }, { x: 25, y: 26 }, { x: 75, y: 26 }];
  if (n === 5) return [{ x: 50, y: 86 }, { x: 22, y: 72 }, { x: 78, y: 72 }, { x: 30, y: 24 }, { x: 70, y: 24 }];
  if (n === 6) return [{ x: 50, y: 86 }, { x: 20, y: 72 }, { x: 80, y: 72 }, { x: 20, y: 28 }, { x: 80, y: 28 }, { x: 50, y: 14 }];
  if (n === 7)
    return [
      { x: 50, y: 88 },
      { x: 22, y: 78 },
      { x: 78, y: 78 },
      { x: 16, y: 54 },
      { x: 84, y: 54 },
      { x: 30, y: 22 },
      { x: 70, y: 22 },
    ];
  if (n === 8)
    return [
      { x: 50, y: 90 },
      { x: 22, y: 80 },
      { x: 78, y: 80 },
      { x: 16, y: 56 },
      { x: 84, y: 56 },
      { x: 22, y: 22 },
      { x: 78, y: 22 },
      { x: 50, y: 12 },
    ];
  return [
    { x: 50, y: 90 },
    { x: 24, y: 82 },
    { x: 76, y: 82 },
    { x: 16, y: 64 },
    { x: 84, y: 64 },
    { x: 16, y: 36 },
    { x: 84, y: 36 },
    { x: 28, y: 18 },
    { x: 72, y: 18 },
  ];
}
