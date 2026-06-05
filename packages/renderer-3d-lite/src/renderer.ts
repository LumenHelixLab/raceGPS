import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { Mesh, StandardMaterial, Color3, VertexData } from '@babylonjs/core';
import { BabylonOverlay } from './overlay/babylonScene.js';
import { CarLayer, type VehicleState } from './overlay/cars/carLayer.js';
import { createRoadMeshes, type CityPackRoad } from './overlay/env/roads.js';
import { createBuildingMeshes, type CityPackBuilding } from './overlay/env/buildings.js';
import { SatelliteGround } from './overlay/env/ground.js';
import { LocalCoords } from './map/coords.js';
import { createRaceMapStyle } from './map/mapStyle.js';
import { registerPMTilesProtocol } from './map/pmtilesProtocol.js';

export type GameMode = 'cruise' | 'race' | 'challenge' | 'hotpursuit' | 'explore';

export interface RaceGPSRendererOptions {
  container: string | HTMLElement;
  center?: { lat: number; lon: number };
  zoom?: number;
}

export class RaceGPSRenderer {
  private container: HTMLElement;
  private map: maplibregl.Map;
  private overlayCanvas?: HTMLCanvasElement;
  private babylon?: BabylonOverlay;
  private carLayer?: CarLayer;
  private coords?: LocalCoords;
  private satellite?: SatelliteGround;
  private envMeshes: { roads?: ReturnType<typeof createRoadMeshes>; buildings?: ReturnType<typeof createBuildingMeshes> } = {};
  private mode: GameMode = 'cruise';
  private streetViewActive = false;
  private lastCarState?: VehicleState;

  constructor(opts: RaceGPSRendererOptions) {
    registerPMTilesProtocol();

    let el = typeof opts.container === 'string'
      ? document.querySelector(opts.container)
      : opts.container;
    if (!el) {
      el = document.createElement('div');
      el.id = typeof opts.container === 'string' ? opts.container.replace(/^#/, '') : 'racegps-map';
      document.body.appendChild(el);
    }
    this.container = el as HTMLElement;
    this.container.style.position = 'absolute';
    this.container.style.inset = '0';

    const center = opts.center ?? { lat: 41.4993, lon: -81.6944 };
    const zoom = opts.zoom ?? 15;

    this.map = new maplibregl.Map({
      container: this.container,
      style: createRaceMapStyle(),
      center: [center.lon, center.lat],
      zoom,
      pitch: 60,
      bearing: -17.6,
      canvasContextAttributes: { antialias: true },
      maxPitch: 85,
    });

    this.map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }));
  }

  /** Enter street-level arcade view: full-screen Babylon overlay + shrunk map minimap */
  enterStreetView(
    roads: CityPackRoad[],
    buildings: CityPackBuilding[],
    originLat: number,
    originLon: number,
  ): void {
    if (this.streetViewActive) return;
    this.streetViewActive = true;

    this.coords = new LocalCoords(originLat, originLon);

    // Create overlay canvas on top
    this.overlayCanvas = document.createElement('canvas');
    this.overlayCanvas.id = 'racegps-babylon-overlay';
    this.overlayCanvas.style.cssText =
      'position:fixed;inset:0;width:100vw;height:100vh;z-index:5;display:block;pointer-events:none;';
    document.body.appendChild(this.overlayCanvas);

    // Shrink map to minimap corner
    this.container.style.cssText =
      'position:fixed;bottom:16px;right:16px;width:240px;height:180px;z-index:10;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.6);border:2px solid rgba(255,255,255,.15);';
    this.map.resize();

    // Start Babylon overlay
    this.babylon = new BabylonOverlay({ canvas: this.overlayCanvas });
    this.babylon.startRenderLoop();

    // Load environment
    this.envMeshes.roads = createRoadMeshes(this.babylon.scene, roads, this.coords);
    this.envMeshes.buildings = createBuildingMeshes(this.babylon.scene, buildings, this.coords);

    // Fallback ground plane
    const groundMat = new StandardMaterial('fallbackGround', this.babylon.scene);
    groundMat.diffuseColor = new Color3(0.1, 0.15, 0.1);
    const ground = new Mesh('ground', this.babylon.scene);
    const positions = [
      -2000, -0.05, -2000,
      2000, -0.05, -2000,
      2000, -0.05, 2000,
      -2000, -0.05, 2000,
    ];
    const indices = [0, 2, 1, 0, 3, 2];
    const normals = [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0];
    const vd = new VertexData();
    vd.positions = positions;
    vd.indices = indices;
    vd.normals = normals;
    vd.applyToMesh(ground);
    ground.material = groundMat;

    this.satellite = new SatelliteGround(this.babylon.scene, this.coords, 17);

    // Car layer
    this.carLayer = new CarLayer(this.babylon.scene);
    this.carLayer.loadCar('/models/kenney-sedan-sports.glb').catch(() => {
      console.warn('[RaceGPSRenderer] Default car failed to load');
    });

    console.log('[RaceGPSRenderer] Street view active');
  }

  exitStreetView(): void {
    if (!this.streetViewActive) return;
    this.streetViewActive = false;

    this.babylon?.stopRenderLoop();
    this.babylon?.dispose();
    this.babylon = undefined;

    this.carLayer?.dispose();
    this.carLayer = undefined;

    this.satellite?.dispose();
    this.satellite = undefined;

    this.envMeshes.roads?.dispose();
    this.envMeshes.buildings?.dispose();
    this.envMeshes = {};

    this.overlayCanvas?.remove();
    this.overlayCanvas = undefined;

    // Restore map full-screen
    this.container.style.cssText = 'position:absolute;inset:0;';
    this.map.resize();
  }

  /** Update the player's car from the arcade physics tick */
  updateCar(state: VehicleState): void {
    this.lastCarState = state;
    if (!this.babylon || !this.carLayer) return;

    this.carLayer.update(state, 1 / 60);
    this.babylon.updateChaseCamera(state.x, state.y, state.z, state.heading, state.speed);
    this.satellite?.update(state.x, state.z);
  }

  async switchCarModel(url: string): Promise<void> {
    await this.carLayer?.loadCar(url);
  }

  setMode(mode: GameMode): void {
    this.mode = mode;
    // TODO: apply semantic layer filters
    console.log('[RaceGPSRenderer] Mode:', mode);
  }

  setMapCenter(lat: number, lon: number, zoom?: number): void {
    const opts: maplibregl.FlyToOptions = { center: [lon, lat], essential: true };
    if (zoom !== undefined) opts.zoom = zoom;
    this.map.flyTo(opts);
  }

  destroy(): void {
    this.exitStreetView();
    this.map.remove();
  }
}
