/**
 * raceGPS Physics Engine
 *
 * Authoritative server-side vehicle physics:
 * - Road-constrained movement (vehicles stay on streets unless crashing)
 * - Crash mechanics (off-road, collisions, obstacle hits)
 * - Obstacle system with collision detection
 * - Vehicle-to-vehicle collision detection
 */

import { haversineMeters, toRad, toDeg, interpolatePoint, type GeoPoint } from './index.js';

// ── Road Network ──────────────────────────────────────────────

export interface RoadSegment {
  start: GeoPoint;
  end: GeoPoint;
  widthMeters: number;
  speedLimit: number; // m/s
}

export interface RoadNetwork {
  segments: RoadSegment[];
}

/**
 * Build a road network from waypoints. Consecutive waypoints become
 * road segments with the given width and speed limit.
 */
export function createRoadNetwork(
  waypoints: GeoPoint[],
  widthMeters = 14,
  speedLimit = 16, // ~58 km/h
): RoadNetwork {
  const segments: RoadSegment[] = [];
  for (let i = 0; i < waypoints.length - 1; i++) {
    segments.push({
      start: waypoints[i],
      end: waypoints[i + 1],
      widthMeters,
      speedLimit,
    });
  }
  return { segments };
}

/**
 * Project a point onto a line segment, returning the closest point
 * and the fractional distance along the segment (0-1).
 */
export function projectPointOnSegment(
  point: GeoPoint,
  start: GeoPoint,
  end: GeoPoint,
): { point: GeoPoint; t: number; distance: number } {
  const dx = end.lon - start.lon;
  const dy = end.lat - start.lat;
  const lenSq = dx * dx + dy * dy;

  if (lenSq === 0) {
    // Degenerate segment: start === end
    const d = haversineMeters(point, start);
    return { point: start, t: 0, distance: d };
  }

  let t = ((point.lon - start.lon) * dx + (point.lat - start.lat) * dy) / lenSq;
  t = Math.max(0, Math.min(1, t));

  const proj: GeoPoint = {
    lat: start.lat + t * dy,
    lon: start.lon + t * dx,
  };

  return { point: proj, t, distance: haversineMeters(point, proj) };
}

/**
 * Find the nearest road point and segment for any given coordinate.
 */
export function nearestRoadPoint(
  point: GeoPoint,
  network: RoadNetwork,
): { point: GeoPoint; segment: RoadSegment; distance: number; index: number } {
  let best: { point: GeoPoint; segment: RoadSegment; distance: number; index: number } | null = null;

  for (let i = 0; i < network.segments.length; i++) {
    const seg = network.segments[i];
    const result = projectPointOnSegment(point, seg.start, seg.end);
    if (!best || result.distance < best.distance) {
      best = { point: result.point, segment: seg, distance: result.distance, index: i };
    }
  }

  // Fallback to first segment start
  if (!best) {
    const seg = network.segments[0];
    return { point: seg.start, segment: seg, distance: 0, index: 0 };
  }

  return best;
}

/**
 * Check if a point is within road width of any segment.
 */
export function isOnRoad(point: GeoPoint, network: RoadNetwork): boolean {
  const nearest = nearestRoadPoint(point, network);
  return nearest.distance <= nearest.segment.widthMeters / 2;
}

// ── Vehicle Physics ───────────────────────────────────────────

export type CrashCause = 'off_road' | 'obstacle' | 'collision' | 'none';

export interface VehiclePhysics {
  playerId: string;
  displayName: string;
  lat: number;
  lon: number;
  heading: number;       // degrees, 0 = north, clockwise
  speed: number;         // m/s
  acceleration: number;  // m/s²
  isCrashed: boolean;
  crashCause: CrashCause;
  crashTimerMs: number;  // remaining crash time
  recoveryTimerMs: number; // remaining recovery (re-entering road)
  onRoad: boolean;
  lastOnRoadPos: GeoPoint;
  lastOnRoadHeading: number;
}

export function createVehiclePhysics(
  playerId: string,
  displayName: string,
  startPos: GeoPoint,
): VehiclePhysics {
  return {
    playerId,
    displayName,
    lat: startPos.lat,
    lon: startPos.lon,
    heading: 0,
    speed: 0,
    acceleration: 0,
    isCrashed: false,
    crashCause: 'none',
    crashTimerMs: 0,
    recoveryTimerMs: 0,
    onRoad: true,
    lastOnRoadPos: { ...startPos },
    lastOnRoadHeading: 0,
  };
}

export interface PhysicsInput {
  throttle: number;  // -1 to 1 (negative = reverse)
  steering: number;  // -1 to 1 (negative = left)
  brake: boolean;
}

// ── Obstacles ─────────────────────────────────────────────────

export type ObstacleType = 'barrier' | 'cone' | 'debris' | 'oil_slick' | 'road_work';

export interface Obstacle {
  id: string;
  point: GeoPoint;
  radius: number;       // collision radius in meters
  type: ObstacleType;
  active: boolean;
  createdAt: number;
}

export function createObstacle(
  id: string,
  point: GeoPoint,
  type: ObstacleType = 'barrier',
  radius = 4,
): Obstacle {
  return { id, point, radius, type, active: true, createdAt: Date.now() };
}

/**
 * Spawn obstacles along a route at random positions near the road.
 */
export function spawnRouteObstacles(
  route: GeoPoint[],
  network: RoadNetwork,
  count: number,
  types: ObstacleType[] = ['barrier', 'cone', 'debris'],
): Obstacle[] {
  const obstacles: Obstacle[] = [];
  const typesArr = types;

  for (let i = 0; i < count; i++) {
    const segIdx = Math.floor(Math.random() * network.segments.length);
    const seg = network.segments[segIdx];
    const t = 0.2 + Math.random() * 0.6; // avoid segment ends
    const proj = projectPointOnSegment(
      { lat: seg.start.lat + t * (seg.end.lat - seg.start.lat),
        lon: seg.start.lon + t * (seg.end.lon - seg.start.lon) },
      seg.start,
      seg.end,
    );

    // Place obstacle offset from road center (on the road surface)
    const offsetDir = Math.random() > 0.5 ? 1 : -1;
    const offsetMeters = (Math.random() * (seg.widthMeters / 3));
    const headingRad = Math.atan2(
      seg.end.lat - seg.start.lat,
      seg.end.lon - seg.start.lon,
    );
    // Perpendicular offset
    const perpHeading = headingRad + (Math.PI / 2) * offsetDir;
    const dLat = (offsetMeters / 111320) * Math.cos(perpHeading);
    const dLon = (offsetMeters / (111320 * Math.cos(toRad(proj.point.lat)))) * Math.sin(perpHeading);

    const type = typesArr[i % typesArr.length];
    obstacles.push(createObstacle(
      `obs_${i}`,
      { lat: proj.point.lat + dLat, lon: proj.point.lon + dLon },
      type,
      type === 'oil_slick' ? 5 : 3 + Math.random() * 2,
    ));
  }

  return obstacles;
}

// ── Physics Simulation ────────────────────────────────────────

export interface PhysicsTickResult {
  position: GeoPoint;
  heading: number;
  speed: number;
  onRoad: boolean;
  isCrashed: boolean;
  crashCause: CrashCause;
  crashJustEnded: boolean;
  hitObstacle: string | null;
  distanceFromRoad: number;
}

const CRASH_DURATION_MS = 3000;
const RECOVERY_DURATION_MS = 2000;
const CRASH_SPIN_SPEED = 180; // degrees/sec
const MAX_SPEED_MS = 22; // ~80 km/h — arcade top speed
const ACCELERATION_MS2 = 6;
const BRAKE_DECEL_MS2 = 12;
const FRICTION_DECEL_MS2 = 2;
const OFF_ROAD_PENALTY_MS2 = 4;
const STEERING_RATE = 90; // degrees/sec at full steering
const STEERING_SPEED_FACTOR = 0.6; // steering efficacy reduces with speed

/**
 * Advance vehicle physics by one tick.
 * @param vehicle Current physics state
 * @param input Driver input (throttle, steering, brake)
 * @param network Road network
 * @param obstacles Active obstacles in the area
 * @param deltaMs Time delta in milliseconds
 * @returns Updated physics state + tick result
 */
export function tickVehiclePhysics(
  vehicle: VehiclePhysics,
  input: PhysicsInput,
  network: RoadNetwork,
  obstacles: Obstacle[],
  deltaMs: number,
): { vehicle: VehiclePhysics; result: PhysicsTickResult } {
  const v = { ...vehicle };
  const deltaSec = deltaMs / 1000;
  let crashJustEnded = false;
  let hitObstacle: string | null = null;

  // ── Crash State ─────────────────────────────────────────
  if (v.isCrashed) {
    v.crashTimerMs -= deltaMs;

    // Spin during crash
    v.heading = (v.heading + CRASH_SPIN_SPEED * deltaSec) % 360;

    // Rapid deceleration during crash
    v.speed = Math.max(0, v.speed - 15 * deltaSec);

    // Check if crash timer expired
    if (v.crashTimerMs <= 0) {
      v.isCrashed = false;
      v.crashCause = 'none';
      crashJustEnded = true;

      // Enter recovery — vehicle is placed back on road
      const nearest = nearestRoadPoint({ lat: v.lat, lon: v.lon }, network);
      v.lat = nearest.point.lat;
      v.lon = nearest.point.lon;
      v.onRoad = true;
      v.recoveryTimerMs = RECOVERY_DURATION_MS;

      // Face along the road segment
      const seg = nearest.segment;
      v.heading = toDeg(Math.atan2(seg.end.lat - seg.start.lat, seg.end.lon - seg.start.lon));
    } else {
      v.onRoad = false;
    }

    return {
      vehicle: v,
      result: {
        position: { lat: v.lat, lon: v.lon },
        heading: v.heading,
        speed: v.speed,
        onRoad: v.onRoad,
        isCrashed: true,
        crashCause: v.crashCause,
        crashJustEnded,
        hitObstacle: null,
        distanceFromRoad: 999,
      },
    };
  }

  // ── Recovery State ──────────────────────────────────────
  if (v.recoveryTimerMs > 0) {
    v.recoveryTimerMs -= deltaMs;
    // Reduced control during recovery
    const controlFactor = Math.min(1, (RECOVERY_DURATION_MS - v.recoveryTimerMs) / RECOVERY_DURATION_MS);
    const effThrottle = input.throttle * controlFactor * 0.6;
    const effSteering = input.steering * controlFactor * 0.4;

    // Apply partial inputs
    if (effThrottle > 0) v.speed = Math.min(MAX_SPEED_MS, v.speed + ACCELERATION_MS2 * deltaSec * effThrottle);
    else if (effThrottle < 0) v.speed = Math.max(0, v.speed - BRAKE_DECEL_MS2 * deltaSec);

    if (input.brake && v.speed > 0) {
      v.speed = Math.max(0, v.speed - BRAKE_DECEL_MS2 * deltaSec);
    }

    // Slow friction
    if (!input.brake && effThrottle === 0) {
      v.speed = Math.max(0, v.speed - FRICTION_DECEL_MS2 * deltaSec);
    }

    // Apply steering (limited)
    const turnRate = STEERING_RATE * effSteering * (1 - v.speed / MAX_SPEED_MS * STEERING_SPEED_FACTOR);
    v.heading = (v.heading + turnRate * deltaSec + 360) % 360;
  } else {
    // ── Normal Input ──────────────────────────────────────
    // Throttle
    if (input.throttle > 0) {
      v.speed = Math.min(MAX_SPEED_MS, v.speed + ACCELERATION_MS2 * deltaSec * input.throttle);
    } else if (input.throttle < 0) {
      v.speed = Math.max(-4, v.speed - ACCELERATION_MS2 * deltaSec * Math.abs(input.throttle));
    }

    // Brake
    if (input.brake && v.speed > 0) {
      v.speed = Math.max(0, v.speed - BRAKE_DECEL_MS2 * deltaSec);
    }

    // Friction
    if (!input.brake && input.throttle === 0) {
      v.speed = Math.max(0, v.speed - FRICTION_DECEL_MS2 * deltaSec);
    }

    // Speed cap
    v.speed = Math.min(MAX_SPEED_MS, v.speed);

    // Steering (rate proportional to speed)
    if (input.steering !== 0 && Math.abs(v.speed) > 0.5) {
      const speedFactor = 1 - (Math.abs(v.speed) / MAX_SPEED_MS) * STEERING_SPEED_FACTOR;
      const turnRate = STEERING_RATE * input.steering * Math.max(0.3, speedFactor);
      v.heading = (v.heading + turnRate * deltaSec + 360) % 360;
    }
  }

  // ── Move Vehicle ─────────────────────────────────────────
  if (Math.abs(v.speed) > 0.01) {
    const headingRad = toRad(v.heading);
    // Speed in degrees per tick (rough lat/lon conversion at ~41.5°N)
    const speedDegPerSec = v.speed / 111320;
    const dLat = speedDegPerSec * Math.cos(headingRad) * deltaSec;
    const dLon = speedDegPerSec * Math.sin(headingRad) / Math.cos(toRad(v.lat)) * deltaSec;
    v.lat += dLat;
    v.lon += dLon;
  }

  // ── Road Check ───────────────────────────────────────────
  const nearest = nearestRoadPoint({ lat: v.lat, lon: v.lon }, network);
  const distFromRoad = nearest.distance;
  v.onRoad = distFromRoad <= nearest.segment.widthMeters / 2;

  // ── Speed Limit Enforcement ──────────────────────────────
  if (v.speed > nearest.segment.speedLimit && v.onRoad) {
    v.speed = Math.max(v.speed - 2 * deltaSec, nearest.segment.speedLimit);
  }

  // ── Off-Road → Crash Check ──────────────────────────────
  if (!v.onRoad && v.speed > 2) {
    v.isCrashed = true;
    v.crashCause = 'off_road';
    v.crashTimerMs = CRASH_DURATION_MS;
    v.speed = Math.max(0, v.speed * 0.7); // speed penalty on crash
  } else if (!v.onRoad && v.speed <= 2) {
    // Slow off-road — gently guide back
    const guidePoint = nearest.point;
    v.lat += (guidePoint.lat - v.lat) * 0.3;
    v.lon += (guidePoint.lon - v.lon) * 0.3;
    v.onRoad = nearestRoadPoint({ lat: v.lat, lon: v.lon }, network).distance <= nearest.segment.widthMeters / 2;
  }

  // ── Obstacle Collision Check ─────────────────────────────
  if (!v.isCrashed) {
    for (const obs of obstacles) {
      if (!obs.active) continue;
      const dist = haversineMeters({ lat: v.lat, lon: v.lon }, obs.point);
      if (dist <= obs.radius && v.speed > 1) {
        // Collision!
        v.isCrashed = true;
        v.crashCause = 'obstacle';
        v.crashTimerMs = CRASH_DURATION_MS;
        v.speed = Math.max(0, v.speed * 0.4); // bigger penalty for obstacles
        hitObstacle = obs.id;

        // Push vehicle away from obstacle
        const angle = Math.atan2(v.lat - obs.point.lat, v.lon - obs.point.lon);
        const pushDeg = 3 / 111320;
        v.lat += pushDeg * Math.sin(angle);
        v.lon += pushDeg * Math.cos(angle) / Math.cos(toRad(v.lat));
        break;
      }
    }
  }

  // ── Track Last On-Road Position ──────────────────────────
  if (v.onRoad && !v.isCrashed) {
    v.lastOnRoadPos = { lat: v.lat, lon: v.lon };
    v.lastOnRoadHeading = v.heading;
  }

  return {
    vehicle: v,
    result: {
      position: { lat: v.lat, lon: v.lon },
      heading: v.heading,
      speed: v.speed,
      onRoad: v.onRoad,
      isCrashed: v.isCrashed,
      crashCause: v.crashCause,
      crashJustEnded,
      hitObstacle,
      distanceFromRoad: distFromRoad,
    },
  };
}

// ── Collision Detection ───────────────────────────────────────

export interface CollisionEvent {
  type: 'vehicle_vehicle' | 'vehicle_obstacle';
  vehicleA: string;
  vehicleB?: string;
  obstacle?: Obstacle;
  point: GeoPoint;
  timestamp: number;
}

/**
 * Check collisions between all vehicles.
 */
export function detectVehicleCollisions(
  vehicles: Map<string, VehiclePhysics>,
  thresholdMeters = 5,
): CollisionEvent[] {
  const events: CollisionEvent[] = [];
  const entries = Array.from(vehicles.values());

  for (let i = 0; i < entries.length; i++) {
    for (let j = i + 1; j < entries.length; j++) {
      const a = entries[i];
      const b = entries[j];
      if (a.isCrashed || b.isCrashed) continue;

      const dist = haversineMeters(
        { lat: a.lat, lon: a.lon },
        { lat: b.lat, lon: b.lon },
      );

      if (dist <= thresholdMeters && (a.speed > 1 || b.speed > 1)) {
        events.push({
          type: 'vehicle_vehicle',
          vehicleA: a.playerId,
          vehicleB: b.playerId,
          point: interpolatePoint(
            { lat: a.lat, lon: a.lon },
            { lat: b.lat, lon: b.lon },
            0.5,
          ),
          timestamp: Date.now(),
        });
      }
    }
  }

  return events;
}

/**
 * Check obstacle collisions for all vehicles.
 */
export function detectObstacleCollisions(
  vehicles: Map<string, VehiclePhysics>,
  obstacles: Obstacle[],
): { vehicleId: string; obstacle: Obstacle }[] {
  const hits: { vehicleId: string; obstacle: Obstacle }[] = [];

  for (const v of Array.from(vehicles.values())) {
    if (v.isCrashed) continue;
    for (const obs of obstacles) {
      if (!obs.active) continue;
      const dist = haversineMeters({ lat: v.lat, lon: v.lon }, obs.point);
      if (dist <= obs.radius && v.speed > 1) {
        hits.push({ vehicleId: v.playerId, obstacle: obs });
      }
    }
  }

  return hits;
}
