/**
 * CityPack loader — converts OSM-derived city data into RoadNetwork + race course definitions.
 */
import type { GeoPoint } from './index.js';
import { createRoadNetwork, type RoadNetwork, type RoadSegment } from './physics.js';

export interface CityPackRoad {
  id: string;
  name: string;
  highway: string;
  oneway: boolean;
  speedLimit: number; // m/s
  width: number;      // meters
  points: GeoPoint[];
  numSegments: number;
}

export interface CityPackBuilding {
  id: string;
  rings: GeoPoint[][];
  height: number;
  minHeight?: number;
  levels?: number;
  roofType?: 'flat' | 'gabled' | 'hipped' | 'pyramidal';
  roofOrientation?: 'along' | 'across';
  hasWindows?: boolean;
}

export interface CityPack {
  name: string;
  version: number;
  center: GeoPoint;
  bounds: { minLat: number; maxLat: number; minLon: number; maxLon: number };
  roads: CityPackRoad[];
  buildings?: CityPackBuilding[];
  stats: {
    totalRoads: number;
    totalSegments: number;
    totalPoints: number;
  };
}

/**
 * Load a CityPack JSON object and build a unified road network from all roads.
 * The network is a flat list of segments; the nearestRoadPoint() function
 * does a brute-force scan (O(n)) which is acceptable for ~10k segments.
 */
export function cityPackToRoadNetwork(pack: CityPack): RoadNetwork {
  const allPoints: GeoPoint[] = [];

  for (const road of pack.roads) {
    for (let i = 0; i < road.points.length; i++) {
      allPoints.push(road.points[i]);
    }
  }

  return createRoadNetwork(allPoints, 14, 16);
}

/**
 * Build a road network with per-segment metadata (speed limits, width, name)
 * instead of using uniform defaults. More accurate for real-world simulation.
 */
export interface RichRoadSegment extends RoadSegment {
  roadName: string;
  highway: string;
  oneway: boolean;
}

export interface RichRoadNetwork {
  segments: RichRoadSegment[];
}

export function cityPackToRichNetwork(pack: CityPack): RichRoadNetwork {
  const segments: RichRoadSegment[] = [];

  for (const road of pack.roads) {
    for (let i = 0; i < road.points.length - 1; i++) {
      segments.push({
        start: road.points[i],
        end: road.points[i + 1],
        widthMeters: road.width,
        speedLimit: road.speedLimit,
        roadName: road.name,
        highway: road.highway,
        oneway: road.oneway,
      });
    }
  }

  return { segments };
}

/**
 * Convert a RichRoadNetwork to a plain RoadNetwork for the physics engine.
 * Physics only needs start/end/width/speedLimit.
 */
export function richToSimple(network: RichRoadNetwork): RoadNetwork {
  return {
    segments: network.segments.map(s => ({
      start: s.start,
      end: s.end,
      widthMeters: s.widthMeters,
      speedLimit: s.speedLimit,
    })),
  };
}

/**
 * Extract a road's geometry as an array of consecutive GeoPoints
 * (flattened from all segments). Useful for rendering.
 */
export function extractRoadGeometries(pack: CityPack): { id: string; name: string; highway: string; points: GeoPoint[] }[] {
  return pack.roads.map(r => ({
    id: r.id,
    name: r.name,
    highway: r.highway,
    points: r.points,
  }));
}

/**
 * Pick a circuit from the city's roads — returns a closed-loop route
 * as a sequence of checkpoint points.
 */
export function extractCircuit(
  pack: CityPack,
  startIndex = 0,
  count = 5,
): { checkpoints: GeoPoint[]; roadIds: string[]; distanceKm: number } {
  const road = pack.roads[startIndex % pack.roads.length];
  const checkpoints: GeoPoint[] = [];
  const roadIds: string[] = [];

  // Pick evenly-spaced points along the road
  const step = Math.max(1, Math.floor(road.points.length / count));
  for (let i = 0; i < count; i++) {
    const idx = Math.min(i * step, road.points.length - 1);
    checkpoints.push(road.points[idx]);
    roadIds.push(road.id);
  }

  // Estimate distance (sum of segment lengths, very rough)
  let distKm = 0;
  for (let i = 1; i < checkpoints.length; i++) {
    const dLat = checkpoints[i].lat - checkpoints[i - 1].lat;
    const dLon = checkpoints[i].lon - checkpoints[i - 1].lon;
    distKm += Math.sqrt(dLat * dLat + dLon * dLon) * 111;
  }

  return { checkpoints, roadIds, distanceKm: Math.round(distKm * 10) / 10 };
}
