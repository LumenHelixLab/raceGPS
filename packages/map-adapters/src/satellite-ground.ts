/**
 * Satellite Tile Ground
 *
 * Fetches ESRI World Imagery tiles and renders them as textured planes
 * in the Three.js scene, creating a real-world ground for driving.
 */

import * as THREE from 'three';
import { LocalCoords } from './street-renderer.js';

const TILE_SIZE = 256; // pixels
const EARTH_RADIUS = 6378137; // Web Mercator
const EARTH_CIRCUMFERENCE = 2 * Math.PI * EARTH_RADIUS;

interface TileCoord {
  x: number;
  y: number;
  z: number;
}

interface TileMesh {
  mesh: THREE.Mesh;
  coord: TileCoord;
}

function latLonToTile(lat: number, lon: number, zoom: number): TileCoord {
  const n = Math.pow(2, zoom);
  const x = Math.floor(((lon + 180) / 360) * n);
  const y = Math.floor(
    ((1 - Math.log(Math.tan((lat * Math.PI) / 180) + 1 / Math.cos((lat * Math.PI) / 180)) / Math.PI) / 2) * n,
  );
  return { x, y, z: zoom };
}

function tileToLatLon(tile: TileCoord): { north: number; south: number; east: number; west: number } {
  const n = Math.pow(2, tile.z);
  const west = (tile.x / n) * 360 - 180;
  const east = ((tile.x + 1) / n) * 360 - 180;
  const north =
    (Math.atan(Math.sinh(Math.PI * (1 - (2 * tile.y) / n))) * 180) / Math.PI;
  const south =
    (Math.atan(Math.sinh(Math.PI * (1 - (2 * (tile.y + 1)) / n))) * 180) / Math.PI;
  return { north, south, east, west };
}

function tileToMeters(tile: TileCoord, coords: LocalCoords): { minX: number; maxX: number; minZ: number; maxZ: number } {
  const bounds = tileToLatLon(tile);
  const nw = coords.toLocal(bounds.north, bounds.west);
  const se = coords.toLocal(bounds.south, bounds.east);
  // In our coords: north = more negative Z, south = less negative Z
  return { minX: nw.x, maxX: se.x, minZ: nw.z, maxZ: se.z };
}

function getTileUrl(tile: TileCoord): string {
  // ESRI World Imagery
  return `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/${tile.z}/${tile.y}/${tile.x}`;
}

export class SatelliteGround {
  private tiles = new Map<string, TileMesh>();
  private loading = new Set<string>();
  private textureLoader = new THREE.TextureLoader();
  private material = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    roughness: 0.9,
    metalness: 0.0,
    side: THREE.DoubleSide,
  });
  private lastCarX = Infinity;
  private lastCarZ = Infinity;

  constructor(
    private scene: THREE.Scene,
    private coords: LocalCoords,
    private zoom = 17,
  ) {
    (this.textureLoader as any).crossOrigin = 'anonymous';
  }

  update(carX: number, carZ: number): void {
    // Throttle: only recompute when car moves ~half a tile
    const tileMeters = (EARTH_CIRCUMFERENCE / Math.pow(2, this.zoom)) * Math.cos(this.coords.originLat * Math.PI / 180);
    const threshold = tileMeters * 0.3;
    if (Math.abs(carX - this.lastCarX) < threshold && Math.abs(carZ - this.lastCarZ) < threshold) return;
    this.lastCarX = carX;
    this.lastCarZ = carZ;

    // Convert car position to lat/lon
    const { lat, lon } = this.coords.toLatLon(carX, carZ);

    // Get center tile
    const centerTile = latLonToTile(lat, lon, this.zoom);

    // Debug: log first update and occasional refreshes
    if (this.tiles.size === 0) {
      console.log('[SatelliteGround] First update at', lat.toFixed(5), lon.toFixed(5), 'center tile:', centerTile, 'tileMeters:', tileMeters.toFixed(1));
    }

    // Load a 3x3 grid around the car
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

    // Remove old tiles
    for (const [key, tileMesh] of this.tiles) {
      if (!tilesToKeep.has(key)) {
        this.scene.remove(tileMesh.mesh);
        (tileMesh.mesh.material as THREE.Material).dispose();
        this.tiles.delete(key);
      }
    }
  }

  private loadTile(tile: TileCoord, key: string): void {
    const url = getTileUrl(tile);

    this.textureLoader.load(
      url,
      (texture) => {
        // If tile was removed while loading, discard
        if (!this.tiles.has(key)) return;

        texture.colorSpace = THREE.SRGBColorSpace;
        texture.magFilter = THREE.LinearFilter;
        texture.minFilter = THREE.LinearFilter;

        const mat = this.material.clone();
        mat.map = texture;

        const mesh = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), mat);
        mesh.rotation.x = -Math.PI / 2;

        // Position and size the tile in world space
        const bounds = tileToMeters(tile, this.coords);
        const width = bounds.maxX - bounds.minX;
        const depth = bounds.maxZ - bounds.minZ;
        const cx = (bounds.minX + bounds.maxX) / 2;
        const cz = (bounds.minZ + bounds.maxZ) / 2;

        mesh.position.set(cx, 0, cz);
        mesh.scale.set(width, depth, 1);
        mesh.receiveShadow = true;

        this.loading.delete(key);
        this.scene.add(mesh);
        this.tiles.set(key, { mesh, coord: tile });
        if (this.tiles.size <= 9) {
          console.log('[SatelliteGround] Tile loaded:', key, 'total:', this.tiles.size);
        }
      },
      undefined,
      (err) => {
        this.loading.delete(key);
        console.warn('[SatelliteGround] Failed to load tile:', url, err);
      },
    );
  }

  dispose(): void {
    for (const tileMesh of this.tiles.values()) {
      this.scene.remove(tileMesh.mesh);
      (tileMesh.mesh.material as THREE.Material).dispose();
    }
    this.tiles.clear();
  }
}
