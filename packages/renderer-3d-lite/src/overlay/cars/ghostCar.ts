import {
  Scene,
  Mesh,
  StandardMaterial,
  Color3,
  VertexData,
  TransformNode,
} from '@babylonjs/core';
import { LocalCoords } from '../../map/coords.js';

export interface GhostPoint {
  lat: number;
  lon: number;
  heading: number;
  speed: number;
  time: number; // seconds from start
}

export class GhostCar {
  private scene: Scene;
  private coords: LocalCoords;
  private node?: TransformNode;
  private route: GhostPoint[] = [];
  private startTime = 0;
  private playing = false;

  constructor(scene: Scene, coords: LocalCoords) {
    this.scene = scene;
    this.coords = coords;
  }

  setRoute(points: GhostPoint[]): void {
    this.route = points;
    if (!this.node) {
      this.node = new TransformNode('ghost', this.scene);
      const mesh = this.createGhostMesh();
      mesh.parent = this.node;
    }
  }

  start(): void {
    this.startTime = performance.now();
    this.playing = true;
  }

  stop(): void {
    this.playing = false;
  }

  update(): void {
    if (!this.playing || !this.node || this.route.length < 2) return;

    const elapsed = (performance.now() - this.startTime) / 1000;
    // Find current segment
    let i = 0;
    while (i < this.route.length - 1 && this.route[i + 1].time < elapsed) {
      i++;
    }
    if (i >= this.route.length - 1) {
      // Restart loop
      this.startTime = performance.now();
      i = 0;
    }

    const a = this.route[i];
    const b = this.route[i + 1];
    const t = Math.max(0, Math.min(1, (elapsed - a.time) / (b.time - a.time)));

    const lat = a.lat + (b.lat - a.lat) * t;
    const lon = a.lon + (b.lon - a.lon) * t;
    const heading = a.heading + ((b.heading - a.heading + 540) % 360 - 180) * t;

    const local = this.coords.toLocal(lat, lon);
    this.node.position.set(local.x, 0.5, local.z);
    this.node.rotation.y = Math.PI - (heading * Math.PI) / 180;
  }

  private createGhostMesh(): Mesh {
    const positions = [
      0, 0.4, 0.8,    // nose
      -0.4, 0, -0.6,  // left rear
      0.4, 0, -0.6,   // right rear
      0, 0.5, 0,      // top
    ];
    const indices = [
      0, 2, 3,  0, 3, 1,
      1, 3, 2,  1, 2, 0,
    ];
    const normals: number[] = [];
    VertexData.ComputeNormals(positions, indices, normals);

    const mesh = new Mesh('ghostMesh', this.scene);
    const vd = new VertexData();
    vd.positions = positions;
    vd.indices = indices;
    vd.normals = normals;
    vd.applyToMesh(mesh);

    const mat = new StandardMaterial('ghostMat', this.scene);
    mat.diffuseColor = new Color3(0.5, 0.8, 1);
    mat.emissiveColor = new Color3(0.2, 0.4, 0.6);
    mat.alpha = 0.5;
    mesh.material = mat;
    return mesh;
  }

  dispose(): void {
    this.node?.dispose();
    this.node = undefined;
    this.route = [];
    this.playing = false;
  }
}
