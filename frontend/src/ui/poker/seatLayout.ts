export function seatPositions(max: number) {
  const positions: Array<{ x: number; y: number }> = [];
  for (let i = 0; i < max; i += 1) {
    const t = (i / max) * Math.PI * 2;
    const rx = 44;
    const ry = 34;
    const x = 50 + Math.cos(t - Math.PI / 2) * rx;
    const y = 52 + Math.sin(t - Math.PI / 2) * ry;
    positions.push({ x, y });
  }
  return positions;
}

