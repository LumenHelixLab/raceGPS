/**
 * Building Generator — ported from streets-gl algorithms
 *
 * Generates Three.js BufferGeometry for building bodies, roofs, and windows
 * from OSM-style building footprints (array of [lon, lat] rings).
 */

import * as THREE from 'three';
import maplibregl from 'maplibre-gl';

// ── Types ────────────────────────────────────────────────────

export interface BuildingFootprint {
  /** Outer ring + optional holes. First ring is outer, rest are holes. */
  rings: { lon: number; lat: number }[][];
  /** Building height in meters */
  height: number;
  /** Base height in meters (for buildings on pylons) */
  minHeight?: number;
  /** Number of floors (affects window density) */
  levels?: number;
  /** Roof type */
  roofType?: 'flat' | 'gabled' | 'hipped' | 'pyramidal';
  /** Roof orientation for gabled roofs: 'along' | 'across' */
  roofOrientation?: 'along' | 'across';
  /** Hex color for walls */
  color?: number;
  /** Hex color for roof */
  roofColor?: number;
  /** Whether windows should be generated */
  hasWindows?: boolean;
}

export interface BuildingGeometrySet {
  body: THREE.BufferGeometry;
  roof: THREE.BufferGeometry;
  windows: THREE.BufferGeometry;
}

// ── Coordinate helpers ───────────────────────────────────────

function mercatorPoint(lon: number, lat: number, altitude = 0): { x: number; y: number; z: number } {
  const c = maplibregl.MercatorCoordinate.fromLngLat([lon, lat], altitude);
  return { x: c.x, y: -c.y, z: c.z };
}

function mercatorScaleAt(lat: number): number {
  const c = maplibregl.MercatorCoordinate.fromLngLat([0, lat]);
  return c.meterInMercatorCoordinateUnits();
}

// ── 2D Geometry helpers ──────────────────────────────────────

function ringArea(ring: { x: number; y: number }[]): number {
  let area = 0;
  for (let i = 0; i < ring.length; i++) {
    const j = (i + 1) % ring.length;
    area += ring[i].x * ring[j].y - ring[j].x * ring[i].y;
  }
  return area * 0.5;
}

function isClockwise(ring: { x: number; y: number }[]): boolean {
  return ringArea(ring) > 0;
}

function reverseRing<T>(ring: T[]): T[] {
  return [...ring].reverse();
}

function polygonCentroid(ring: { x: number; y: number }[]): { x: number; y: number } {
  let cx = 0, cy = 0, a = 0;
  for (let i = 0; i < ring.length; i++) {
    const j = (i + 1) % ring.length;
    const cross = ring[i].x * ring[j].y - ring[j].x * ring[i].y;
    cx += (ring[i].x + ring[j].x) * cross;
    cy += (ring[i].y + ring[j].y) * cross;
    a += cross;
  }
  a *= 0.5;
  const factor = 1 / (6 * a);
  return { x: cx * factor, y: cy * factor };
}

function ringBounds(ring: { x: number; y: number }[]): { minX: number; maxX: number; minY: number; maxY: number } {
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  for (const p of ring) {
    minX = Math.min(minX, p.x);
    maxX = Math.max(maxX, p.x);
    minY = Math.min(minY, p.y);
    maxY = Math.max(maxY, p.y);
  }
  return { minX, maxX, minY, maxY };
}

function distance2D(a: { x: number; y: number }, b: { x: number; y: number }): number {
  const dx = a.x - b.x;
  const dy = a.y - b.y;
  return Math.sqrt(dx * dx + dy * dy);
}

function normalize2D(v: { x: number; y: number }): { x: number; y: number } {
  const len = Math.sqrt(v.x * v.x + v.y * v.y) || 1;
  return { x: v.x / len, y: v.y / len };
}

function perpendicular2D(v: { x: number; y: number }): { x: number; y: number } {
  return { x: -v.y, y: v.x };
}

function lerp2D(a: { x: number; y: number }, b: { x: number; y: number }, t: number): { x: number; y: number } {
  return { x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t };
}

function triangleNormal(a: THREE.Vector3, b: THREE.Vector3, c: THREE.Vector3): THREE.Vector3 {
  const ab = new THREE.Vector3().subVectors(b, a);
  const ac = new THREE.Vector3().subVectors(c, a);
  return new THREE.Vector3().crossVectors(ab, ac).normalize();
}

// ── Wall Generation (ported from streets-gl WallsBuilder) ────

interface WallSegment {
  a: { x: number; y: number };
  b: { x: number; y: number };
  length: number;
}

function getWallSegments(ring: { x: number; y: number }[]): WallSegment[] {
  const segments: WallSegment[] = [];
  for (let i = 0; i < ring.length; i++) {
    const j = (i + 1) % ring.length;
    const a = ring[i];
    const b = ring[j];
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    const length = Math.sqrt(dx * dx + dy * dy);
    if (length > 1e-9) {
      segments.push({ a, b, length });
    }
  }
  return segments;
}

function generateWalls(
  ring: { x: number; y: number }[],
  minHeightM: number,
  heightM: number,
  levels: number,
  hasWindows: boolean,
  scale: number,
): {
  positions: number[];
  normals: number[];
  colors: number[];
  windowPositions: number[];
} {
  const positions: number[] = [];
  const normals: number[] = [];
  const colors: number[] = [];
  const windowPositions: number[] = [];

  const segments = getWallSegments(ring);
  const wallHeight = heightM - minHeightM;
  const levelHeight = wallHeight / Math.max(1, levels);

  // Window dimensions in meters
  const windowWidthM = 1.2;
  const windowHeightM = 1.6;
  const windowBottomM = 0.9; // distance from floor
  const windowSpacingM = 0.4; // spacing between windows

  for (const seg of segments) {
    const dx = seg.b.x - seg.a.x;
    const dy = seg.b.y - seg.a.y;
    const segLen = seg.length;
    const normal = normalize2D(perpendicular2D({ x: dx, y: dy }));
    const nx = normal.x;
    const ny = normal.y;

    // Wall quad: two triangles
    const baseZ = minHeightM * scale;
    const topZ = heightM * scale;

    const ax = seg.a.x, ay = seg.a.y;
    const bx = seg.b.x, by = seg.b.y;

    // Tri 1: a-base, b-base, a-top
    positions.push(ax, ay, baseZ, bx, by, baseZ, ax, ay, topZ);
    normals.push(nx, ny, 0, nx, ny, 0, nx, ny, 0);

    // Tri 2: b-base, b-top, a-top
    positions.push(bx, by, baseZ, bx, by, topZ, ax, ay, topZ);
    normals.push(nx, ny, 0, nx, ny, 0, nx, ny, 0);

    // Windows on this segment
    if (hasWindows && levels > 0) {
      const segLenM = segLen / scale;
      const usableWidth = segLenM - windowSpacingM;
      const windowCount = Math.max(1, Math.floor(usableWidth / (windowWidthM + windowSpacingM)));
      const actualSpacing = (segLenM - windowCount * windowWidthM) / (windowCount + 1);

      for (let level = 0; level < levels; level++) {
        for (let wi = 0; wi < windowCount; wi++) {
          const wLeftM = actualSpacing + wi * (windowWidthM + actualSpacing);
          const wRightM = wLeftM + windowWidthM;
          const wBottomM = level * levelHeight + windowBottomM;
          const wTopM = Math.min(wBottomM + windowHeightM, (level + 1) * levelHeight - 0.1);

          if (wTopM <= wBottomM) continue;

          const t0 = wLeftM / segLenM;
          const t1 = wRightM / segLenM;

          const p0 = lerp2D(seg.a, seg.b, t0);
          const p1 = lerp2D(seg.a, seg.b, t1);

          const z0 = (minHeightM + wBottomM) * scale;
          const z1 = (minHeightM + wTopM) * scale;

          // Window is a thin quad slightly inset from wall
          const inset = 0.02 * scale;
          const ix = nx * inset;
          const iy = ny * inset;

          // Two triangles per window
          windowPositions.push(
            p0.x + ix, p0.y + iy, z0,
            p1.x + ix, p1.y + iy, z0,
            p0.x + ix, p0.y + iy, z1,
            p1.x + ix, p1.y + iy, z0,
            p1.x + ix, p1.y + iy, z1,
            p0.x + ix, p0.y + iy, z1,
          );
        }
      }
    }
  }

  return { positions, normals, colors, windowPositions };
}

// ── Roof Generation ──────────────────────────────────────────

function generateFlatRoof(
  ring: { x: number; y: number }[],
  heightM: number,
  scale: number,
): { positions: number[]; normals: number[] } {
  const positions: number[] = [];
  const normals: number[] = [];
  const z = heightM * scale;

  // Simple ear-clipping triangulation for convex-ish polygons
  // For robustness, we use a fan from the centroid
  const center = polygonCentroid(ring);
  for (let i = 0; i < ring.length; i++) {
    const j = (i + 1) % ring.length;
    positions.push(center.x, center.y, z, ring[i].x, ring[i].y, z, ring[j].x, ring[j].y, z);
    normals.push(0, 0, 1, 0, 0, 1, 0, 0, 1);
  }

  return { positions, normals };
}

function generateGabledRoof(
  ring: { x: number; y: number }[],
  heightM: number,
  roofHeightM: number,
  scale: number,
  orientation: 'along' | 'across',
): { positions: number[]; normals: number[] } {
  const positions: number[] = [];
  const normals: number[] = [];

  const bounds = ringBounds(ring);
  const center = polygonCentroid(ring);
  const ridgeZ = (heightM + roofHeightM) * scale;
  const baseZ = heightM * scale;

  // Determine ridge direction
  const dx = bounds.maxX - bounds.minX;
  const dy = bounds.maxY - bounds.minY;
  const isWiderX = dx > dy;
  const ridgeAlongX = orientation === 'along' ? isWiderX : !isWiderX;

  // For each edge, find where it meets the ridge plane
  for (let i = 0; i < ring.length; i++) {
    const j = (i + 1) % ring.length;
    const a = ring[i];
    const b = ring[j];

    if (ridgeAlongX) {
      // Ridge is horizontal (constant y)
      // Find intersection of edge with ridge y
      const t = (center.y - a.y) / (b.y - a.y);
      if (t >= 0 && t <= 1) {
        const ridgePoint = lerp2D(a, b, t);
        // Two triangles: a-ridgePoint-b and a-base-b... no wait
        // For gabled roof, each edge connects to the ridge
        // Actually simpler: triangulate from ridge line
      }
    }
  }

  // Simpler approach: create ridge line through center, project vertices up
  for (let i = 0; i < ring.length; i++) {
    const j = (i + 1) % ring.length;
    const a = ring[i];
    const b = ring[j];

    let ra: { x: number; y: number; z: number };
    let rb: { x: number; y: number; z: number };

    if (ridgeAlongX) {
      // Ridge at center.y
      ra = { x: a.x, y: center.y, z: ridgeZ };
      rb = { x: b.x, y: center.y, z: ridgeZ };
    } else {
      // Ridge at center.x
      ra = { x: center.x, y: a.y, z: ridgeZ };
      rb = { x: center.x, y: b.y, z: ridgeZ };
    }

    // Two roof faces for this edge
    // Face 1: a -> b -> rb
    const n1 = triangleNormal(
      new THREE.Vector3(a.x, a.y, baseZ),
      new THREE.Vector3(b.x, b.y, baseZ),
      new THREE.Vector3(rb.x, rb.y, ridgeZ),
    );
    positions.push(a.x, a.y, baseZ, b.x, b.y, baseZ, rb.x, rb.y, ridgeZ);
    normals.push(n1.x, n1.y, n1.z, n1.x, n1.y, n1.z, n1.x, n1.y, n1.z);

    // Face 2: a -> rb -> ra
    const n2 = triangleNormal(
      new THREE.Vector3(a.x, a.y, baseZ),
      new THREE.Vector3(rb.x, rb.y, ridgeZ),
      new THREE.Vector3(ra.x, ra.y, ridgeZ),
    );
    positions.push(a.x, a.y, baseZ, rb.x, rb.y, ridgeZ, ra.x, ra.y, ridgeZ);
    normals.push(n2.x, n2.y, n2.z, n2.x, n2.y, n2.z, n2.x, n2.y, n2.z);
  }

  return { positions, normals };
}

function generateHippedRoof(
  ring: { x: number; y: number }[],
  heightM: number,
  roofHeightM: number,
  scale: number,
): { positions: number[]; normals: number[] } {
  const positions: number[] = [];
  const normals: number[] = [];

  const center = polygonCentroid(ring);
  const ridgeZ = (heightM + roofHeightM) * scale;
  const baseZ = heightM * scale;

  // Fan triangulation from center peak to each edge
  for (let i = 0; i < ring.length; i++) {
    const j = (i + 1) % ring.length;
    const a = ring[i];
    const b = ring[j];

    const n = triangleNormal(
      new THREE.Vector3(a.x, a.y, baseZ),
      new THREE.Vector3(b.x, b.y, baseZ),
      new THREE.Vector3(center.x, center.y, ridgeZ),
    );

    positions.push(a.x, a.y, baseZ, b.x, b.y, baseZ, center.x, center.y, ridgeZ);
    normals.push(n.x, n.y, n.z, n.x, n.y, n.z, n.x, n.y, n.z);
  }

  return { positions, normals };
}

function generatePyramidalRoof(
  ring: { x: number; y: number }[],
  heightM: number,
  roofHeightM: number,
  scale: number,
): { positions: number[]; normals: number[] } {
  // Same as hipped for simple implementation
  return generateHippedRoof(ring, heightM, roofHeightM, scale);
}

// ── Main Building Generator ──────────────────────────────────

export function generateBuildingGeometry(
  footprint: BuildingFootprint,
  referenceLat: number,
): BuildingGeometrySet {
  const scale = mercatorScaleAt(referenceLat);

  // Convert rings to mercator coords
  const mercatorRings = footprint.rings.map(ring =>
    ring.map(p => {
      const m = mercatorPoint(p.lon, p.lat);
      return { x: m.x, y: m.y };
    })
  );

  // Ensure outer ring is counter-clockwise and holes are clockwise
  const outerRing = mercatorRings[0];
  const fixedRings = [isClockwise(outerRing) ? outerRing : reverseRing(outerRing)];
  for (let i = 1; i < mercatorRings.length; i++) {
    const hole = mercatorRings[i];
    fixedRings.push(isClockwise(hole) ? reverseRing(hole) : hole);
  }

  const heightM = footprint.height || 12;
  const minHeightM = footprint.minHeight || 0;
  const levels = footprint.levels || Math.max(1, Math.round(heightM / 4));
  const roofType = footprint.roofType || 'flat';
  const hasWindows = footprint.hasWindows !== false && heightM - minHeightM > 3;

  const allBodyPositions: number[] = [];
  const allBodyNormals: number[] = [];
  const allRoofPositions: number[] = [];
  const allRoofNormals: number[] = [];
  const allWindowPositions: number[] = [];

  for (const ring of fixedRings) {
    if (ring.length < 3) continue;

    // Walls
    const walls = generateWalls(ring, minHeightM, heightM, levels, hasWindows, scale);
    allBodyPositions.push(...walls.positions);
    allBodyNormals.push(...walls.normals);
    allWindowPositions.push(...walls.windowPositions);

    // Roof
    const roofHeightM = roofType === 'flat' ? 0 : Math.min(heightM * 0.3, 8);
    let roof: { positions: number[]; normals: number[] };

    switch (roofType) {
      case 'gabled':
        roof = generateGabledRoof(ring, heightM, roofHeightM, scale, footprint.roofOrientation || 'along');
        break;
      case 'hipped':
        roof = generateHippedRoof(ring, heightM, roofHeightM, scale);
        break;
      case 'pyramidal':
        roof = generatePyramidalRoof(ring, heightM, roofHeightM, scale);
        break;
      case 'flat':
      default:
        roof = generateFlatRoof(ring, heightM, scale);
        break;
    }

    allRoofPositions.push(...roof.positions);
    allRoofNormals.push(...roof.normals);
  }

  const bodyGeom = new THREE.BufferGeometry();
  bodyGeom.setAttribute('position', new THREE.Float32BufferAttribute(allBodyPositions, 3));
  bodyGeom.setAttribute('normal', new THREE.Float32BufferAttribute(allBodyNormals, 3));

  const roofGeom = new THREE.BufferGeometry();
  roofGeom.setAttribute('position', new THREE.Float32BufferAttribute(allRoofPositions, 3));
  roofGeom.setAttribute('normal', new THREE.Float32BufferAttribute(allRoofNormals, 3));

  const windowGeom = new THREE.BufferGeometry();
  if (allWindowPositions.length > 0) {
    windowGeom.setAttribute('position', new THREE.Float32BufferAttribute(allWindowPositions, 3));
    windowGeom.computeVertexNormals();
  }

  return { body: bodyGeom, roof: roofGeom, windows: windowGeom };
}

// ── Batch Generator ──────────────────────────────────────────

export function generateCityBuildings(
  buildings: BuildingFootprint[],
  referenceLat: number,
): {
  body: THREE.BufferGeometry;
  roof: THREE.BufferGeometry;
  windows: THREE.BufferGeometry;
} {
  const bodyGeoms: THREE.BufferGeometry[] = [];
  const roofGeoms: THREE.BufferGeometry[] = [];
  const windowGeoms: THREE.BufferGeometry[] = [];

  for (const b of buildings) {
    const g = generateBuildingGeometry(b, referenceLat);
    if (g.body.attributes.position && (g.body.attributes.position as THREE.BufferAttribute).count > 0) {
      bodyGeoms.push(g.body);
    }
    if (g.roof.attributes.position && (g.roof.attributes.position as THREE.BufferAttribute).count > 0) {
      roofGeoms.push(g.roof);
    }
    if (g.windows.attributes.position && (g.windows.attributes.position as THREE.BufferAttribute).count > 0) {
      windowGeoms.push(g.windows);
    }
  }

  return {
    body: mergeBufferGeometries(bodyGeoms),
    roof: mergeBufferGeometries(roofGeoms),
    windows: mergeBufferGeometries(windowGeoms),
  };
}

function mergeBufferGeometries(geoms: THREE.BufferGeometry[]): THREE.BufferGeometry {
  if (geoms.length === 0) {
    const empty = new THREE.BufferGeometry();
    empty.setAttribute('position', new THREE.Float32BufferAttribute([], 3));
    empty.setAttribute('normal', new THREE.Float32BufferAttribute([], 3));
    return empty;
  }
  if (geoms.length === 1) return geoms[0];

  let posLen = 0;
  for (const g of geoms) {
    posLen += (g.attributes.position as THREE.BufferAttribute).count * 3;
  }

  const positions = new Float32Array(posLen);
  const normals = new Float32Array(posLen);
  let offset = 0;

  for (const g of geoms) {
    const pos = g.attributes.position as THREE.BufferAttribute;
    const nor = g.attributes.normal as THREE.BufferAttribute;
    const count = pos.count;

    for (let i = 0; i < count; i++) {
      positions[offset + i * 3] = pos.getX(i);
      positions[offset + i * 3 + 1] = pos.getY(i);
      positions[offset + i * 3 + 2] = pos.getZ(i);

      if (nor) {
        normals[offset + i * 3] = nor.getX(i);
        normals[offset + i * 3 + 1] = nor.getY(i);
        normals[offset + i * 3 + 2] = nor.getZ(i);
      }
    }
    offset += count * 3;
  }

  const merged = new THREE.BufferGeometry();
  merged.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  merged.setAttribute('normal', new THREE.BufferAttribute(normals, 3));
  return merged;
}

// ── MapLibre Vector Tile Feature Parser ──────────────────────

/**
 * Convert MapLibre vector tile building features to BuildingFootprint array.
 * Call this after the map has loaded buildings tiles.
 */
export function extractBuildingsFromMapLibre(
  map: maplibregl.Map,
  sourceName = 'openmaptiles',
  sourceLayer = 'building',
): BuildingFootprint[] {
  const features = map.querySourceFeatures(sourceName, { sourceLayer });
  const buildings: BuildingFootprint[] = [];

  for (const f of features) {
    const geom = f.geometry;
    if (!geom || geom.type !== 'Polygon') continue;

    const coords = (geom as GeoJSON.Polygon).coordinates;
    const rings = coords.map(ring =>
      ring.map(([lon, lat]) => ({ lon, lat })),
    );

    const height = (f.properties?.render_height as number) || (f.properties?.height as number) || 12;
    const minHeight = (f.properties?.render_min_height as number) || (f.properties?.min_height as number) || 0;
    const levels = (f.properties?.building_levels as number) || Math.max(1, Math.round(height / 4));

    // Simple heuristic: large buildings get flat roofs, smaller residential get gabled
    const area = ringArea(rings[0].map(p => mercatorPoint(p.lon, p.lat)));
    const isLarge = area / (mercatorScaleAt(map.getCenter().lat) ** 2) > 500; // > 500 sq m
    const roofType: BuildingFootprint['roofType'] = isLarge ? 'flat' : 'gabled';

    // Random-ish color based on building id
    const hue = ((f.id as number) || 0) % 360;
    const color = new THREE.Color().setHSL(hue / 360, 0.15, 0.35).getHex();
    const roofColor = new THREE.Color().setHSL(hue / 360, 0.1, 0.25).getHex();

    buildings.push({
      rings,
      height,
      minHeight,
      levels,
      roofType,
      color,
      roofColor,
      hasWindows: true,
    });
  }

  return buildings;
}
