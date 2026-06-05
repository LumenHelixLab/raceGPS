/**
 * raceGPS MapLibre 3D Adapter
 *
 * - Renders a real vector-map base with 3D building extrusions and terrain
 * - Embeds a Three.js custom layer for vehicles, roads, and effects
 * - Syncs Three.js camera with MapLibre camera automatically
 */

import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import * as THREE from 'three';
import type { MapAdapter, MapPoint } from './index.js';
import {
  type BuildingFootprint,
  extractBuildingsFromMapLibre,
  generateCityBuildings,
} from './building-generator.js';
import { StreetRenderer, type CityPackRoad as StreetRoad, type CityPackBuilding as StreetBuilding, type VehicleState as StreetVehicleState } from './street-renderer.js';

export interface CityPackRoad {
  id: string;
  name: string;
  highway: string;
  points: { lat: number; lon: number }[];
  width?: number;
}

export interface CityPackBuilding {
  id: string;
  rings: { lat: number; lon: number }[][];
  height: number;
  minHeight?: number;
  levels?: number;
  roofType?: 'flat' | 'gabled' | 'hipped' | 'pyramidal';
  roofOrientation?: 'along' | 'across';
  hasWindows?: boolean;
}

export interface CityPack {
  name: string;
  center: { lat: number; lon: number };
  roads: CityPackRoad[];
  buildings?: CityPackBuilding[];
}

// ── Hybrid Satellite Style ───────────────────────────────────

function createHybridSatelliteStyle(): maplibregl.StyleSpecification {
  return {
    version: 8,
    sources: {
      satellite: {
        type: 'raster',
        tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],
        tileSize: 256,
        attribution: 'Esri',
        maxzoom: 19,
      },
      openmaptiles: {
        type: 'vector',
        url: 'https://tiles.openfreemap.org/planet',
      },
    },
    glyphs: 'https://tiles.openfreemap.org/fonts/{fontstack}/{range}.pbf',
    layers: [
      // Satellite base
      { id: 'satellite', type: 'raster', source: 'satellite', minzoom: 0, maxzoom: 22 },
      // Water
      { id: 'water', type: 'fill', source: 'openmaptiles', 'source-layer': 'water',
        paint: { 'fill-color': 'rgba(20,60,100,0.6)' } },
      // Roads
      { id: 'road-motorway', type: 'line', source: 'openmaptiles', 'source-layer': 'transportation',
        filter: ['all', ['==', '$type', 'LineString'], ['in', 'class', 'motorway', 'trunk']],
        paint: { 'line-color': '#ffaa33', 'line-width': ['interpolate', ['linear'], ['zoom'], 10, 1, 16, 4] } },
      { id: 'road-primary', type: 'line', source: 'openmaptiles', 'source-layer': 'transportation',
        filter: ['all', ['==', '$type', 'LineString'], ['in', 'class', 'primary', 'secondary']],
        paint: { 'line-color': '#ffdd88', 'line-width': ['interpolate', ['linear'], ['zoom'], 10, 0.5, 16, 3] } },
      { id: 'road-street', type: 'line', source: 'openmaptiles', 'source-layer': 'transportation',
        filter: ['all', ['==', '$type', 'LineString'], ['in', 'class', 'tertiary', 'minor', 'service']],
        paint: { 'line-color': '#ffffff', 'line-width': ['interpolate', ['linear'], ['zoom'], 13, 0.5, 16, 2], 'line-opacity': 0.8 } },
      // Road labels
      { id: 'road-label', type: 'symbol', source: 'openmaptiles', 'source-layer': 'transportation_name',
        minzoom: 13,
        layout: { 'text-field': '{name}', 'text-size': 11, 'text-font': ['Noto Sans Regular'] },
        paint: { 'text-color': '#ffffff', 'text-halo-color': '#000000', 'text-halo-width': 1.5 } },
      // Place labels
      { id: 'place-label', type: 'symbol', source: 'openmaptiles', 'source-layer': 'place',
        minzoom: 10,
        layout: { 'text-field': '{name}', 'text-size': 14, 'text-font': ['Noto Sans Bold'] },
        paint: { 'text-color': '#ffffff', 'text-halo-color': '#000000', 'text-halo-width': 2 } },
    ],
  } as maplibregl.StyleSpecification;
}

// ── Coordinate Conversions ───────────────────────────────────

/**
 * Convert lat/lon to Three.js world space aligned with MapLibre's custom layer.
 *
 * MapLibre's `defaultProjectionData.mainMatrix` transforms mercator coordinates
 * in range [0..1] to clip space.  Three.js is right-handed (Y=north, Z=up)
 * while MapLibre mercator is left-handed (Y=south, Z=up).  The camera's
 * `matrixWorldInverse` applies a Y-flip so this helper can return a
 * right-handed vector.
 */
export function geoToWorld(_map: maplibregl.Map, point: MapPoint, altitude = 0): THREE.Vector3 {
  const coord = maplibregl.MercatorCoordinate.fromLngLat([point.lon, point.lat], altitude);
  return new THREE.Vector3(coord.x, -coord.y, coord.z);
}

/** Return the mercator scale factor (units per meter) at a given lat/lon. */
function meterScaleAt(point: MapPoint): number {
  const coord = maplibregl.MercatorCoordinate.fromLngLat([point.lon, point.lat]);
  return coord.meterInMercatorCoordinateUnits();
}

// ── Three.js Custom Layer ────────────────────────────────────

interface GameScene {
  scene: THREE.Scene;
  camera: THREE.Camera;
  renderer: THREE.WebGLRenderer;
  markers: Map<string, THREE.Object3D>;
  roadMesh?: THREE.Mesh;
  routeMesh?: THREE.Mesh;
  buildingBody?: THREE.Mesh;
  buildingRoof?: THREE.Mesh;
  buildingWindows?: THREE.Mesh;
  root: THREE.Group;
}

class ThreeJsLayer implements maplibregl.CustomLayerInterface {
  id = 'racegps-game-layer';
  type = 'custom' as const;
  renderingMode = '3d' as const;

  private map?: maplibregl.Map;
  private gl?: WebGL2RenderingContext | WebGLRenderingContext;
  private game?: GameScene;
  private onLoad?: () => void;
  private renderedOnce = false;

  constructor(onLoad?: () => void) {
    this.onLoad = onLoad;
  }

  onAdd(map: maplibregl.Map, gl: WebGL2RenderingContext | WebGLRenderingContext): void {
    console.log('[ThreeJsLayer] onAdd called');
    this.map = map;
    this.gl = gl;

    const scene = new THREE.Scene();
    const root = new THREE.Group();
    scene.add(root);

    // Midnight Club night vibe: blue moon + warm street ambience
    const hemiLight = new THREE.HemisphereLight(0xaaccff, 0x1a1a2e, 0.6);
    scene.add(hemiLight);

    const dirLight = new THREE.DirectionalLight(0xffaa77, 0.4);
    dirLight.position.set(100, 200, 100);
    scene.add(dirLight);

    // Camera is driven by MapLibre's projection matrix each frame.
    const camera = new THREE.Camera();
    camera.matrixAutoUpdate = false;

    const renderer = new THREE.WebGLRenderer({
      canvas: map.getCanvas(),
      context: gl as WebGLRenderingContext,
      antialias: true,
    });
    renderer.autoClear = false;
    renderer.shadowMap.enabled = true;

    // Add a debug cube at the map center to verify Three.js rendering
    const debugCube = new THREE.Mesh(
      new THREE.BoxGeometry(0.0001, 0.0001, 0.0001),
      new THREE.MeshBasicMaterial({ color: 0xff0000 }),
    );
    debugCube.name = 'debug-cube';
    root.add(debugCube);

    this.game = {
      scene,
      camera,
      renderer,
      markers: new Map(),
      root,
    };

    console.log('[ThreeJsLayer] scene created, markers:', this.game.markers.size);
    this.onLoad?.();
  }

  onRemove(): void {
    this.game?.renderer.dispose();
    this.game = undefined;
    this.map = undefined;
  }

  prerender(): void {
    // Scene mutations happen via adapter API; no per-frame scene work needed here.
  }

  render(
    _gl: WebGL2RenderingContext | WebGLRenderingContext,
    options: maplibregl.CustomRenderMethodInput,
  ): void {
    if (!this.game || !this.map) return;
    const { renderer, scene, camera } = this.game;
    // Debug: log first render
    if (!this.renderedOnce) {
      console.log('[ThreeJsLayer] first render, markers:', this.game.markers.size);
      this.renderedOnce = true;
    }

    // Use the official mercator-scaled matrix so objects can be placed in
    // [0..1] mercator coordinates.
    camera.projectionMatrix = new THREE.Matrix4().fromArray(
      options.defaultProjectionData.mainMatrix as number[],
    );
    camera.projectionMatrixInverse.copy(camera.projectionMatrix).invert();

    // Handedness fix: MapLibre mercator is left-handed (X=east, Y=south, Z=up).
    // Three.js world space is right-handed (X=east, Y=north, Z=up).
    // This scale matrix flips Y so the two coordinate systems align.
    camera.matrixWorldInverse = new THREE.Matrix4().makeScale(1, -1, 1);
    camera.matrixWorld.copy(camera.matrixWorldInverse).invert(); // self-inverse
    camera.updateMatrixWorld(false);

    renderer.state.reset();
    renderer.render(scene, camera);
    this.map.triggerRepaint();
  }

  getGameScene(): GameScene | undefined {
    return this.game;
  }
}

// ── MapLibre 3D Adapter ──────────────────────────────────────

export interface MapLibre3DOptions {
  center?: MapPoint;
  zoom?: number;
  pitch?: number;
  bearing?: number;
  citypack?: CityPack;
}

export class MapLibre3DAdapter implements MapAdapter {
  name = 'maplibre-3d';
  private map?: maplibregl.Map;
  private container?: HTMLElement;
  private layer?: ThreeJsLayer;
  private options: MapLibre3DOptions;
  private gameReady = false;
  private pendingRoads?: CityPackRoad[];
  private htmlMarkers = new Map<string, maplibregl.Marker>();

  // Street-level arcade renderer
  private streetRenderer?: StreetRenderer;
  private streetCanvas?: HTMLCanvasElement;
  private minimapContainer?: HTMLElement;

  constructor(options: MapLibre3DOptions = {}) {
    this.options = options;
  }

  mount(container: string | HTMLElement): void {
    let el: HTMLElement | null = typeof container === 'string' ? document.querySelector(container) : container;
    if (!el) {
      el = document.createElement('div');
      el.id = typeof container === 'string' ? container.replace(/^#/, '') : 'racegps-map';
      el.style.position = 'absolute';
      el.style.inset = '0';
      document.body.appendChild(el);
    }
    this.container = el;

    const center = this.options.center ?? { lat: 41.4993, lon: -81.6944 };
    const zoom = this.options.zoom ?? 15;
    const pitch = this.options.pitch ?? 60;
    const bearing = this.options.bearing ?? -17.6;

    this.map = new maplibregl.Map({
      container: el,
      style: createHybridSatelliteStyle(),
      center: [center.lon, center.lat],
      zoom,
      pitch,
      bearing,
      canvasContextAttributes: { antialias: true },
      maxPitch: 85,
    });

    this.map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }));

    this.map.on('load', () => {
      this.addBuildings();
      this.addGameLayer();
    });
  }

  private addBuildings(): void {
    if (!this.map) return;

    // If citypack has buildings, use them directly
    if (this.options.citypack?.buildings && this.options.citypack.buildings.length > 0) {
      this.generateAndAddBuildings(this.options.citypack.buildings);
      return;
    }

    // Wait for building tiles to load, then extract from vector tiles
    const tryExtract = () => {
      const buildings = extractBuildingsFromMapLibre(this.map!);
      if (buildings.length === 0) return false;
      this.generateAndAddBuildings(buildings);
      return true;
    };

    if (!tryExtract()) {
      let attempts = 0;
      const interval = setInterval(() => {
        attempts++;
        if (tryExtract() || attempts > 30) {
          clearInterval(interval);
          if (attempts > 30) {
            const synthetic = this.generateSyntheticBuildings();
            if (synthetic.length > 0) this.generateAndAddBuildings(synthetic);
          }
        }
      }, 500);
    }
  }

  private generateSyntheticBuildings(): BuildingFootprint[] {
    const pack = this.options.citypack;
    if (!pack || pack.roads.length === 0) return [];

    const buildings: BuildingFootprint[] = [];
    const rng = (seed: number) => {
      const x = Math.sin(seed) * 10000;
      return x - Math.floor(x);
    };

    let buildingId = 0;
    for (const road of pack.roads) {
      if (road.points.length < 2) continue;
      // Skip small residential roads
      if (road.highway === 'service' || road.highway === 'footway') continue;

      for (let i = 0; i < road.points.length - 1; i += 3) {
        const a = road.points[i];
        const b = road.points[i + 1];

        // Perpendicular offset from road
        const dLat = b.lat - a.lat;
        const dLon = b.lon - a.lon;
        const len = Math.sqrt(dLat * dLat + dLon * dLon);
        if (len < 1e-9) continue;

        const perpLat = -dLon / len * 0.0002;
        const perpLon = dLat / len * 0.0002;

        const midLat = (a.lat + b.lat) / 2;
        const midLon = (a.lon + b.lon) / 2;

        // Building on one side of road
        const offset = rng(buildingId) > 0.5 ? 1 : -1;
        const baseLat = midLat + perpLat * offset;
        const baseLon = midLon + perpLon * offset;

        const widthM = 10 + rng(buildingId + 1) * 15;
        const depthM = 10 + rng(buildingId + 2) * 15;
        const heightM = 6 + rng(buildingId + 3) * 24;

        // Convert meters to degrees (approx)
        const latScale = 1 / 111000;
        const lonScale = 1 / (111000 * Math.cos(midLat * Math.PI / 180));
        const wDeg = widthM * latScale;
        const dDeg = depthM * lonScale;

        const ring = [
          { lon: baseLon - dDeg, lat: baseLat - wDeg },
          { lon: baseLon + dDeg, lat: baseLat - wDeg },
          { lon: baseLon + dDeg, lat: baseLat + wDeg },
          { lon: baseLon - dDeg, lat: baseLat + wDeg },
        ];

        const roofTypes: BuildingFootprint['roofType'][] = ['flat', 'gabled', 'hipped'];
        const hue = (buildingId * 137.5) % 360;
        const color = new THREE.Color().setHSL(hue / 360, 0.12, 0.32 + rng(buildingId + 4) * 0.15).getHex();

        buildings.push({
          rings: [ring],
          height: heightM,
          levels: Math.max(1, Math.round(heightM / 4)),
          roofType: roofTypes[Math.floor(rng(buildingId + 5) * roofTypes.length)],
          roofOrientation: rng(buildingId + 6) > 0.5 ? 'along' : 'across',
          color,
          roofColor: new THREE.Color().setHSL(hue / 360, 0.08, 0.22).getHex(),
          hasWindows: true,
        });

        buildingId++;
        if (buildingId > 400) break;
      }
      if (buildingId > 400) break;
    }

    return buildings;
  }

  private generateAndAddBuildings(buildings: BuildingFootprint[]): void {
    const scene = this.layer?.getGameScene();
    const map = this.map;
    if (!scene || !map) return;

    // Clean up old meshes
    scene.buildingBody?.removeFromParent();
    scene.buildingRoof?.removeFromParent();
    scene.buildingWindows?.removeFromParent();
    scene.buildingBody?.geometry.dispose();
    scene.buildingRoof?.geometry.dispose();
    scene.buildingWindows?.geometry.dispose();
    (scene.buildingBody?.material as THREE.Material | undefined)?.dispose();
    (scene.buildingRoof?.material as THREE.Material | undefined)?.dispose();
    (scene.buildingWindows?.material as THREE.Material | undefined)?.dispose();

    const refLat = map.getCenter().lat;
    const geoms = generateCityBuildings(buildings, refLat);

    // Body material: rough concrete/plaster
    const bodyMat = new THREE.MeshStandardMaterial({
      color: 0x4a5568,
      roughness: 0.85,
      metalness: 0.05,
    });

    // Roof material: slightly darker
    const roofMat = new THREE.MeshStandardMaterial({
      color: 0x2d3748,
      roughness: 0.9,
      metalness: 0.1,
    });

    // Window material: emissive for night glow
    const windowMat = new THREE.MeshStandardMaterial({
      color: 0xffeeaa,
      emissive: 0xffaa44,
      emissiveIntensity: 0.8,
      roughness: 0.2,
      metalness: 0.8,
    });

    scene.buildingBody = new THREE.Mesh(geoms.body, bodyMat);
    scene.buildingBody.name = 'buildings-body';
    scene.root.add(scene.buildingBody);

    scene.buildingRoof = new THREE.Mesh(geoms.roof, roofMat);
    scene.buildingRoof.name = 'buildings-roof';
    scene.root.add(scene.buildingRoof);

    if ((geoms.windows.attributes.position as THREE.BufferAttribute)?.count > 0) {
      scene.buildingWindows = new THREE.Mesh(geoms.windows, windowMat);
      scene.buildingWindows.name = 'buildings-windows';
      scene.root.add(scene.buildingWindows);
    }

    console.log(`[raceGPS] Generated ${buildings.length} buildings: bodies=${(geoms.body.attributes.position as THREE.BufferAttribute).count} verts, roofs=${(geoms.roof.attributes.position as THREE.BufferAttribute).count} verts, windows=${(geoms.windows.attributes.position as THREE.BufferAttribute)?.count || 0} verts`);
  }

  private addTerrain(): void {
    // Terrain source disabled — demotiles endpoint returning 404s
  }

  private addGameLayer(): void {
    if (!this.map) return;

    this.layer = new ThreeJsLayer(() => {
      this.gameReady = true;
      if (this.pendingRoads) {
        this.drawRoads(this.pendingRoads);
        this.pendingRoads = undefined;
      }
    });

    this.map.addLayer(this.layer);
  }

  setCenter(point: MapPoint, zoom?: number): void {
    if (!this.map) return;
    const opts: maplibregl.FlyToOptions = { center: [point.lon, point.lat], essential: true };
    if (zoom !== undefined) opts.zoom = zoom;
    this.map.flyTo(opts);
  }

  jumpTo(point: MapPoint, zoom?: number, bearing?: number, pitch?: number): void {
    if (!this.map) return;
    this.map.jumpTo({ center: [point.lon, point.lat], zoom, bearing, pitch });
  }

  setBearing(bearing: number): void {
    this.map?.setBearing(bearing);
  }

  setPitch(pitch: number): void {
    this.map?.setPitch(pitch);
  }

  /**
   * Street-level chase camera.
   * Positions the map camera low and behind the vehicle for a racing-game feel.
   * Call this every frame from the drive tick.
   */
  syncStreetCamera(lat: number, lon: number, heading: number, speed: number): void {
    if (!this.map) {
      console.warn('[MapLibre3DAdapter] syncStreetCamera: no map');
      return;
    }

    const speedFactor = Math.min(speed / 30, 1);

    // True dash-cam: very close to ground, looking forward
    // Zoom 19 = ~76m altitude, zoom 20 = ~38m altitude
    const zoom = 19.2 - speedFactor * 0.7;

    // Pitch 80-84°: 80° = looking 10° down from horizontal, 84° = looking 6° down
    const pitch = 80 + speedFactor * 4;

    // Center point only 8-15m ahead — camera sits right behind the car
    const lookAheadM = 8 + speedFactor * 7;

    const headingRad = heading * (Math.PI / 180);
    const dLat = (lookAheadM * Math.cos(headingRad)) / 111320;
    const dLon = (lookAheadM * Math.sin(headingRad)) / (111320 * Math.cos(lat * Math.PI / 180));

    const centerLat = lat + dLat;
    const centerLon = lon + dLon;

    this.map.jumpTo({
      center: [centerLon, centerLat],
      zoom,
      pitch,
      bearing: heading,
    });
  }

  upsertPlayerMarker(playerId: string, point: MapPoint, _label: string, heading = 0): void {
    const scene = this.layer?.getGameScene();
    const map = this.map;
    const scale = meterScaleAt(point);
    console.log('[MapLibre3DAdapter] upsertPlayerMarker', playerId, point, 'scale:', scale, 'heading:', heading);

    // ── HTML Marker (fallback — always visible) ──
    let htmlMarker = this.htmlMarkers.get(playerId);
    if (!htmlMarker) {
      const el = document.createElement('div');
      el.className = 'racegps-car-marker';
      el.innerHTML = `
        <div class="car-body"></div>
        <div class="car-arrow"></div>
      `;
      htmlMarker = new maplibregl.Marker({ element: el, anchor: 'center', pitchAlignment: 'map', rotationAlignment: 'map' });
      htmlMarker.setLngLat([point.lon, point.lat]);
      htmlMarker.addTo(map!);
      this.htmlMarkers.set(playerId, htmlMarker);
      console.log('[MapLibre3DAdapter] HTML marker created for', playerId);
    } else {
      htmlMarker.setLngLat([point.lon, point.lat]);
    }
    // Rotate the marker element to match heading
    const markerEl = htmlMarker.getElement();
    if (markerEl) {
      markerEl.style.transform = `${markerEl.style.transform.replace(/rotate\([^)]*\)/, '')} rotate(${heading}deg)`;
    }

    // ── Three.js marker (3D layer) ──
    if (scene && map) {
      let marker = scene.markers.get(playerId);
      if (!marker) {
        marker = createPlaceholderCar();
        scene.root.add(marker);
        scene.markers.set(playerId, marker);
      }
      marker.position.copy(geoToWorld(map, point, 0.5));
      marker.scale.setScalar(scale);
      marker.rotation.set(0, 0, -heading * (Math.PI / 180));
    }
  }

  removePlayerMarker(playerId: string): void {
    const scene = this.layer?.getGameScene();
    const marker = scene?.markers.get(playerId);
    if (marker && scene) {
      marker.removeFromParent();
      scene.markers.delete(playerId);
    }
    const htmlMarker = this.htmlMarkers.get(playerId);
    if (htmlMarker) {
      htmlMarker.remove();
      this.htmlMarkers.delete(playerId);
    }
  }

  drawRoute(points: MapPoint[]): void {
    const scene = this.layer?.getGameScene();
    const map = this.map;
    if (!scene || !map || points.length < 2) return;

    scene.routeMesh?.removeFromParent();
    scene.routeMesh?.geometry.dispose();
    (scene.routeMesh?.material as THREE.Material | undefined)?.dispose();

    const curve = new THREE.CatmullRomCurve3(points.map(p => geoToWorld(map, p, 2)));
    const scale = meterScaleAt(points[0]);
    const geom = new THREE.TubeGeometry(curve, Math.max(2, points.length * 3), 1.5 * scale, 8, false);
    const mat = new THREE.MeshBasicMaterial({
      color: 0x00ffcc,
      transparent: true,
      opacity: 0.35,
      side: THREE.DoubleSide,
    });

    scene.routeMesh = new THREE.Mesh(geom, mat);
    scene.routeMesh.name = 'route';
    scene.root.add(scene.routeMesh);
  }

  /** Render CityPack buildings as detailed Three.js meshes. */
  drawBuildings(buildings: CityPackBuilding[]): void {
    this.generateAndAddBuildings(buildings);
  }

  /** Render CityPack road network as a flat 3D mesh. */
  drawRoads(roads: CityPackRoad[]): void {
    if (!this.gameReady) {
      this.pendingRoads = roads;
      return;
    }
    const scene = this.layer?.getGameScene();
    const map = this.map;
    if (!scene || !map) return;

    scene.roadMesh?.removeFromParent();
    scene.roadMesh?.geometry.dispose();
    (scene.roadMesh?.material as THREE.Material | undefined)?.dispose();

    const geometries: THREE.BufferGeometry[] = [];

    for (const road of roads) {
      if (road.points.length < 2) continue;
      const scale = meterScaleAt(road.points[0]);
      const width = (road.width ?? 8) * scale;
      const pts = road.points.map(p => geoToWorld(map, p, 0.05));

      // Build a strip of quads along the polyline
      const positions: number[] = [];
      const indices: number[] = [];
      let vertOffset = 0;

      for (let i = 0; i < pts.length - 1; i++) {
        const a = pts[i];
        const b = pts[i + 1];
        const dir = new THREE.Vector3().subVectors(b, a).normalize();
        const perp = new THREE.Vector3(-dir.y, dir.x, 0).multiplyScalar(width / 2);

        const v0 = new THREE.Vector3().addVectors(a, perp);
        const v1 = new THREE.Vector3().subVectors(a, perp);
        const v2 = new THREE.Vector3().subVectors(b, perp);
        const v3 = new THREE.Vector3().addVectors(b, perp);

        positions.push(
          v0.x, v0.y, v0.z,
          v1.x, v1.y, v1.z,
          v2.x, v2.y, v2.z,
          v3.x, v3.y, v3.z,
        );

        indices.push(
          vertOffset, vertOffset + 1, vertOffset + 2,
          vertOffset, vertOffset + 2, vertOffset + 3,
        );
        vertOffset += 4;
      }

      if (positions.length === 0) continue;

      const geom = new THREE.BufferGeometry();
      geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
      geom.setIndex(indices);
      geom.computeVertexNormals();
      geometries.push(geom);
    }

    if (geometries.length === 0) return;

    const merged = mergeGeometries(geometries);
    const material = new THREE.MeshStandardMaterial({
      color: 0x2d3436,
      roughness: 0.9,
      metalness: 0.1,
    });

    scene.roadMesh = new THREE.Mesh(merged, material);
    scene.roadMesh.name = 'roads';
    scene.root.add(scene.roadMesh);
  }

  // ── Street-Level Arcade View ────────────────────────────

  enterStreetView(roads: StreetRoad[], buildings: StreetBuilding[], originLat: number, originLon: number): void {
    if (this.streetRenderer) return;

    // Create full-screen canvas for street view
    this.streetCanvas = document.createElement('canvas');
    this.streetCanvas.id = 'racegps-street-view';
    this.streetCanvas.style.cssText = 'position:fixed;inset:0;width:100vw;height:100vh;z-index:5;display:block;';
    document.body.appendChild(this.streetCanvas);

    // Shrink map to minimap (bottom-right corner)
    if (this.container) {
      this.container.style.cssText = 'position:fixed;bottom:16px;right:16px;width:240px;height:180px;z-index:10;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.6);border:2px solid rgba(255,255,255,.15);';
    }
    this.map?.resize();

    this.streetRenderer = new StreetRenderer(this.streetCanvas);
    this.streetRenderer.loadCity(roads, buildings, originLat, originLon);
    // Load Kenney sedan-sports as default player car
    this.streetRenderer.loadCarModel('/models/kenney-sedan-sports.glb').catch(() => {
      console.warn('[MapLibre3DAdapter] Failed to load car model, using fallback');
    });
    this.streetRenderer.start();
    console.log('[MapLibre3DAdapter] Street view active');
  }

  exitStreetView(): void {
    this.streetRenderer?.stop();
    this.streetRenderer = undefined;
    this.streetCanvas?.remove();
    this.streetCanvas = undefined;
    if (this.container) {
      this.container.style.cssText = '';
    }
    this.map?.resize();
  }

  updateStreetView(state: StreetVehicleState, _speed: number): void {
    if (!this.streetRenderer) return;
    this.streetRenderer.setTargetState(state);
  }

  switchCarModel(url: string): void {
    this.streetRenderer?.switchCarModel(url).catch((err) => {
      console.warn('[MapLibre3DAdapter] Failed to switch car model:', err);
    });
  }

  destroy(): void {
    this.exitStreetView();
    this.map?.remove();
    this.map = undefined;
    this.layer = undefined;
  }
}

// ── Helpers ──────────────────────────────────────────────────

function createPlaceholderCar(): THREE.Group {
  const group = new THREE.Group();

  // Body: 1.8m wide, 4.2m long, 1.4m tall
  const body = new THREE.Mesh(
    new THREE.BoxGeometry(1.8, 4.2, 1.4),
    new THREE.MeshStandardMaterial({ color: 0xff3333, roughness: 0.3, metalness: 0.7, emissive: 0xff0000, emissiveIntensity: 0.2 }),
  );
  body.position.z = 0.7;
  group.add(body);

  // Bright nose cone for direction
  const nose = new THREE.Mesh(
    new THREE.ConeGeometry(0.35, 1.0, 8),
    new THREE.MeshStandardMaterial({ color: 0xffdd00, emissive: 0xffaa00, emissiveIntensity: 0.8 }),
  );
  nose.position.set(0, 2.6, 0.7);
  group.add(nose);

  // Large floating arrow above car (visible from distance)
  const arrow = new THREE.Mesh(
    new THREE.ConeGeometry(0.5, 1.0, 4),
    new THREE.MeshBasicMaterial({ color: 0x00ff00 }),
  );
  arrow.position.z = 3.5;
  group.add(arrow);

  // Underglow
  const glow = new THREE.PointLight(0x00ffff, 2, 15);
  glow.position.z = -0.2;
  group.add(glow);

  // Headlights
  const headLightL = new THREE.SpotLight(0xffffff, 3, 50, 0.6, 0.5, 1);
  headLightL.position.set(-0.6, 1.8, 0.9);
  headLightL.target.position.set(-0.6, 4, 0.9);
  group.add(headLightL);
  group.add(headLightL.target);

  const headLightR = headLightL.clone();
  headLightR.position.set(0.6, 1.8, 0.9);
  headLightR.target.position.set(0.6, 4, 0.9);
  group.add(headLightR);
  group.add(headLightR.target);

  return group;
}

function mergeGeometries(geometries: THREE.BufferGeometry[]): THREE.BufferGeometry {
  if (geometries.length === 1) return geometries[0];

  let totalVerts = 0;
  let totalIndices = 0;
  for (const g of geometries) {
    totalVerts += g.attributes.position.count;
    totalIndices += g.index ? g.index.count : g.attributes.position.count;
  }

  const mergedPos = new Float32Array(totalVerts * 3);
  const mergedIndex = new Uint32Array(totalIndices);
  let vOffset = 0;
  let iOffset = 0;

  for (const g of geometries) {
    const pos = g.attributes.position.array as Float32Array;
    mergedPos.set(pos, vOffset * 3);

    const count = g.attributes.position.count;
    if (g.index) {
      const idx = g.index.array;
      for (let i = 0; i < idx.length; i++) {
        mergedIndex[iOffset + i] = (idx[i] as number) + vOffset;
      }
      iOffset += idx.length;
    } else {
      for (let i = 0; i < count; i++) {
        mergedIndex[iOffset + i] = vOffset + i;
      }
      iOffset += count;
    }
    vOffset += count;
  }

  const result = new THREE.BufferGeometry();
  result.setAttribute('position', new THREE.BufferAttribute(mergedPos, 3));
  result.setIndex(new THREE.BufferAttribute(mergedIndex, 1));
  result.computeVertexNormals();
  return result;
}
