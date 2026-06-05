export interface MapPoint { lat: number; lon: number }

export interface MapAdapter {
  name: string;
  mount(container: HTMLElement): void;
  setCenter(point: MapPoint, zoom?: number): void;
  upsertPlayerMarker(playerId: string, point: MapPoint, label: string): void;
  removePlayerMarker(playerId: string): void;
  drawRoute(points: MapPoint[]): void;
  destroy(): void;
}

export { MockMapAdapter } from './mock.js';
export { MapLibre3DAdapter, geoToWorld } from './maplibre-3d.js';
export type { CityPack, CityPackRoad, MapLibre3DOptions } from './maplibre-3d.js';
