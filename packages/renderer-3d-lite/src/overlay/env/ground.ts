import { Scene, Mesh, StandardMaterial, Color3, VertexData, Texture } from '@babylonjs/core';
import { LocalCoords } from '../../map/coords.js';

const TILE_SIZE = 256;
const EARTH_RADIUS = 6378137;
const EARTH_CIRCUMFERENCE = 2 * Math.PI * EARTH_RADIUS;

interface TileCoord { x: number; y: number; z: number; }

function latLonToTile(lat: number, lon: number, zoom: number): TileCoord {
  const n = Math.pow(2, zoom);
  const x = Math.floor(((lon + 180) / 360) * n);
  const y = Math.floor(
    ((1 - Math.log(Math.tan((lat * Math.PI) / 180) + 1 / Math.cos((lat * Math.PI) / 180)) / Math.PI) / 2) * n,
  );
  return { x, y, z: zoom };
}

function tileToLatLon(tile: TileCoord) {
  const n = Math.pow(2, tile.z);
  const west = (tile.x / n) * 360 - 180;
  const east = ((tile.x + 1) / n) * 360 - 180;
  const north = (Math.atan(Math.sinh(Math.PI * (1 - (2 * tile.y) / n))) * 180) / Math.PI;
  const south = (Math.atan(Math.sinh(Math.PI * (1 - (2 * (tile.y + 1)) / n))) * 180) / Math.PI;
  return { north, south, east, west };
}

function tileToMeters(tile: TileCoord, coords: LocalCoords) {
  const bounds = tileToLatLon(tile);
  const nw = coords.toLocal(bounds.north, bounds.west);
  const se = coords.toLocal(bounds.south, bounds.east);
  return { minX: nw.x, maxX: se.x, minZ: nw.z, maxZ: se.z };
}

function getTileUrl(tile: TileCoord): string {
  return `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/${tile.z}/${tile.y}/${tile.x}`;
}

export class SatelliteGround {
  private tiles = new Map<string, Mesh>();
  private loading = new Set<string>();
  private lastCarX = Infinity;
  private lastCarZ = Infinity;

  constructor(
    private scene: Scene,
    private coords: LocalCoords,
    private zoom = 17,
  ) {}

  update(carX: number, carZ: number): void {
    const tileMeters = (EARTH_CIRCUMFERENCE / Math.pow(2, this.zoom)) * Math.cos(this.coords.originLat * Math.PI / 180);
    const threshold = tileMeters * 0.3;
    if (Math.abs(carX - this.lastCarX) < threshold && Math.abs(carZ - this.lastCarZ) < threshold) return;
    this.lastCarX = carX;
    this.lastCarZ = carZ;

    const { lat, lon } = this.coords.toLatLon(carX, carZ);
    const centerTile = latLonToTile(lat, lon, this.zoom);

    if (this.tiles.size === 0) {
      console.log('[SatelliteGround] Loading tiles at', lat.toFixed(5), lon.toFixed(5));
    }

    const tilesToKeep = new Set<string>();
    for (let dx = -1; dx <= 1; dx++) {
      for (let dy = -1; dy <= 1; dy++) {
        const tile = { x: centerTile.x + dx, y: centerTile.y + dy, z: this.zoom };
        const key = `${tile.z}/${tile.x}/${tile.y}`;
        tilesToKeep.add(key);
        if (!this.tiles.has(key) && !this.loading.has(key)) {
          this.loading.add(key);
          this.loadTile(tile, key);
        }
      }
    }

    for (const [key, mesh] of this.tiles) {
      if (!tilesToKeep.has(key)) {
        mesh.dispose();
        this.tiles.delete(key);
      }
    }
  }

  private loadTile(tile: TileCoord, key: string): void {
    const url = getTileUrl(tile);
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      this.loading.delete(key);
      const tex = new Texture(img.src, this.scene);
      tex.wrapU = Texture.WRAP_ADDRESSMODE;
      tex.wrapV = Texture.WRAP_ADDRESSMODE;

      const mat = new StandardMaterial('tileMat_' + key, this.scene);
      mat.diffuseTexture = tex;
      mat.specularColor = new Color3(0, 0, 0);

      const mesh = new Mesh('tile_' + key, this.scene);
      const bounds = tileToMeters(tile, this.coords);
      const width = bounds.maxX - bounds.minX;
      const depth = bounds.maxZ - bounds.minZ;
      const cx = (bounds.minX + bounds.maxX) / 2;
      const cz = (bounds.minZ + bounds.maxZ) / 2;

      const positions = [
        cx - width/2, 0, cz - depth/2,
        cx + width/2, 0, cz - depth/2,
        cx + width/2, 0, cz + depth/2,
        cx - width/2, 0, cz + depth/2,
      ];
      const indices = [0, 2, 1, 0, 3, 2];
      const normals = [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0];
      const uvs = [0, 0, 1, 0, 1, 1, 0, 1];

      const vd = new VertexData();
      vd.positions = positions;
      vd.indices = indices;
      vd.normals = normals;
      vd.uvs = uvs;
      vd.applyToMesh(mesh);
      mesh.material = mat;

      this.scene.addMesh(mesh);
      this.tiles.set(key, mesh);
      if (this.tiles.size <= 9) {
        console.log('[SatelliteGround] Tile loaded:', key, 'total:', this.tiles.size);
      }
    };
    img.onerror = () => {
      this.loading.delete(key);
      console.warn('[SatelliteGround] Failed to load tile:', url);
    };
    img.src = url;
  }

  dispose(): void {
    for (const mesh of this.tiles.values()) {
      mesh.dispose();
    }
    this.tiles.clear();
    this.loading.clear();
  }
}
