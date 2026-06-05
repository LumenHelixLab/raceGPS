import {
  Scene,
  Mesh,
  StandardMaterial,
  Color3,
  VertexData,
  Vector3,
  Animation,
} from '@babylonjs/core';
import { LocalCoords } from '../../map/coords.js';

export interface CheckpointDef {
  id: string;
  lat: number;
  lon: number;
  heading: number;
}

export class CheckpointGates {
  private scene: Scene;
  private coords: LocalCoords;
  private gates = new Map<string, Mesh>();

  constructor(scene: Scene, coords: LocalCoords) {
    this.scene = scene;
    this.coords = coords;
  }

  add(def: CheckpointDef): void {
    if (this.gates.has(def.id)) return;

    const local = this.coords.toLocal(def.lat, def.lon);
    const headingRad = (def.heading * Math.PI) / 180;

    // Procedural arch gate
    const arch = this.createArch();
    arch.position.set(local.x, 0, local.z);
    arch.rotation.y = -headingRad;

    this.gates.set(def.id, arch);
  }

  remove(id: string): void {
    const gate = this.gates.get(id);
    if (gate) {
      gate.dispose();
      this.gates.delete(id);
    }
  }

  clear(): void {
    for (const gate of this.gates.values()) {
      gate.dispose();
    }
    this.gates.clear();
  }

  private createArch(): Mesh {
    const positions: number[] = [];
    const indices: number[] = [];
    const normals: number[] = [];
    const segments = 16;
    const width = 8;
    const height = 5;
    const thickness = 0.3;
    let idx = 0;

    // Two vertical pillars + arch top
    // Left pillar
    for (let y = 0; y <= height; y += height / 4) {
      positions.push(
        -width/2, y, -thickness/2,
        -width/2, y, thickness/2,
        -width/2 + thickness, y, thickness/2,
        -width/2 + thickness, y, -thickness/2,
      );
      indices.push(
        idx, idx + 1, idx + 2,
        idx, idx + 2, idx + 3,
      );
      idx += 4;
    }

    // Right pillar
    for (let y = 0; y <= height; y += height / 4) {
      positions.push(
        width/2 - thickness, y, -thickness/2,
        width/2 - thickness, y, thickness/2,
        width/2, y, thickness/2,
        width/2, y, -thickness/2,
      );
      indices.push(
        idx, idx + 1, idx + 2,
        idx, idx + 2, idx + 3,
      );
      idx += 4;
    }

    // Arch top (semicircle)
    for (let i = 0; i <= segments; i++) {
      const angle = Math.PI * (i / segments); // 0 to PI
      const cx = Math.cos(angle) * (width/2 - thickness/2);
      const cy = height + Math.sin(angle) * 2;
      positions.push(cx - thickness/2, cy, -thickness/2);
      positions.push(cx + thickness/2, cy, -thickness/2);
      positions.push(cx + thickness/2, cy, thickness/2);
      positions.push(cx - thickness/2, cy, thickness/2);
      if (i < segments) {
        indices.push(
          idx, idx + 1, idx + 2,
          idx, idx + 2, idx + 3,
          idx + 4, idx + 6, idx + 5,
          idx + 4, idx + 7, idx + 6,
        );
      }
      idx += 4;
    }

    VertexData.ComputeNormals(positions, indices, normals);

    const mesh = new Mesh('checkpointGate', this.scene);
    const vd = new VertexData();
    vd.positions = positions;
    vd.indices = indices;
    vd.normals = normals;
    vd.applyToMesh(mesh);

    const mat = new StandardMaterial('gateMat', this.scene);
    mat.diffuseColor = new Color3(0.2, 0.9, 0.4);
    mat.emissiveColor = new Color3(0.1, 0.5, 0.2);
    mat.specularColor = new Color3(0, 0, 0);
    mat.alpha = 0.7;
    mesh.material = mat;

    return mesh;
  }

  dispose(): void {
    this.clear();
  }
}
