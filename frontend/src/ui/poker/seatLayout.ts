export function seatPositions(max: number) {
  const n = Math.max(2, Math.min(9, Math.floor(max)));
  if (n === 2) return [{ x: 36, y: 80 }, { x: 64, y: 80 }];
  if (n === 3) return [{ x: 50, y: 80 }, { x: 26, y: 34 }, { x: 74, y: 34 }];
  if (n === 4) return [{ x: 26, y: 76 }, { x: 74, y: 76 }, { x: 26, y: 24 }, { x: 74, y: 24 }];
  if (n === 5) return [{ x: 50, y: 80 }, { x: 22, y: 70 }, { x: 78, y: 70 }, { x: 30, y: 28 }, { x: 70, y: 28 }];
  if (n === 6) return [{ x: 50, y: 80 }, { x: 20, y: 70 }, { x: 80, y: 70 }, { x: 20, y: 34 }, { x: 80, y: 34 }, { x: 50, y: 22 }];
  if (n === 7)
    return [
      { x: 50, y: 80 },
      { x: 20, y: 72 },
      { x: 80, y: 72 },
      { x: 14, y: 54 },
      { x: 86, y: 54 },
      { x: 30, y: 28 },
      { x: 70, y: 28 },
    ];
  if (n === 8)
    return [
      { x: 50, y: 80 },
      { x: 22, y: 72 },
      { x: 78, y: 72 },
      { x: 14, y: 55 },
      { x: 86, y: 55 },
      { x: 22, y: 28 },
      { x: 78, y: 28 },
      { x: 50, y: 22 },
    ];
  return [
    { x: 50, y: 80 },
    { x: 24, y: 72 },
    { x: 76, y: 72 },
    { x: 14, y: 62 },
    { x: 86, y: 62 },
    { x: 14, y: 38 },
    { x: 86, y: 38 },
    { x: 28, y: 24 },
    { x: 72, y: 24 },
  ];
}
