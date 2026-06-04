export interface GeoPoint { lat: number; lon: number }
export interface RouteObject { id: string; type: string; point: GeoPoint; score: number; radiusMeters: number }
export interface Checkpoint { id: string; point: GeoPoint; radiusMeters: number }

export function haversineMeters(a: GeoPoint, b: GeoPoint): number {
  const r = 6371000;
  const dLat = toRad(b.lat - a.lat);
  const dLon = toRad(b.lon - a.lon);
  const lat1 = toRad(a.lat);
  const lat2 = toRad(b.lat);
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon / 2) ** 2;
  return 2 * r * Math.asin(Math.sqrt(h));
}

function toRad(deg: number): number { return deg * Math.PI / 180; }

export function isWithinRadius(player: GeoPoint, target: GeoPoint, radiusMeters: number): boolean {
  return haversineMeters(player, target) <= radiusMeters;
}

export function scorePickup(baseScore: number, heatMultiplier = 1): number {
  return Math.round(baseScore * Math.max(1, heatMultiplier));
}

export function computeHeat(currentHeat: number, delta: number): number {
  return Math.max(0, Math.min(6, currentHeat + delta));
}

export function validatePursuitTag(cop: GeoPoint, runner: GeoPoint, captureRadiusMeters = 8): boolean {
  return isWithinRadius(cop, runner, captureRadiusMeters);
}
