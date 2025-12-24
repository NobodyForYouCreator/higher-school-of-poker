export function seatPositions(max: number) {
  const n = Math.max(2, Math.min(9, Math.floor(max)));
  if (n === 2) return [{ x: 36, y: 82 }, { x: 64, y: 82 }];
  if (n === 3) return [{ x: 50, y: 84 }, { x: 26, y: 30 }, { x: 74, y: 30 }];
  if (n === 4) return [{ x: 26, y: 78 }, { x: 74, y: 78 }, { x: 26, y: 22 }, { x: 74, y: 22 }];
  if (n === 5) return [{ x: 50, y: 84 }, { x: 22, y: 72 }, { x: 78, y: 72 }, { x: 30, y: 24 }, { x: 70, y: 24 }];
  if (n === 6) return [{ x: 50, y: 84 }, { x: 20, y: 72 }, { x: 80, y: 72 }, { x: 20, y: 30 }, { x: 80, y: 30 }, { x: 50, y: 16 }];
  if (n === 7)
    return [
      { x: 50, y: 84 },
      { x: 20, y: 76 },
      { x: 80, y: 76 },
      { x: 14, y: 54 },
      { x: 86, y: 54 },
      { x: 30, y: 24 },
      { x: 70, y: 24 },
    ];
  if (n === 8)
    return [
      { x: 50, y: 84 },
      { x: 22, y: 76 },
      { x: 78, y: 76 },
      { x: 14, y: 55 },
      { x: 86, y: 55 },
      { x: 22, y: 24 },
      { x: 78, y: 24 },
      { x: 50, y: 16 },
    ];
  return [
    { x: 50, y: 84 },
    { x: 24, y: 76 },
    { x: 76, y: 76 },
    { x: 14, y: 62 },
    { x: 86, y: 62 },
    { x: 14, y: 38 },
    { x: 86, y: 38 },
    { x: 28, y: 20 },
    { x: 72, y: 20 },
  ];
}
