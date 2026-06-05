import {
  Scene,
  Mesh,
  StandardMaterial,
  Color3,
  VertexData,
  Vector3,
} from '@babylonjs/core';
import { LocalCoords } from '../../map/coords.js';

export type PickupType = 'coin' | 'boost' | 'badge' | 'token' | 'evidence';

export interface PickupDef {
  id: string;
  lat: number;
  lon: number;
  type: PickupType;
}

const TYPE_COLORS: Record<PickupType, Color3> = {
  coin: new Color3(1, 0.84, 0),
  boost: new Color3(1, 0.2, 0.2),
  badge: new Color3(0.2, 0.6, 1),
  token: new Color3(0.8, 0.2, 0.8),
  evidence: new Color3(0.2, 0.9, 0.4),
};

export class PickupLayer {
  private scene: Scene;
  private coords: LocalCoords;
  private pickups = new Map<string, Mesh>();
  private time = 0;

  constructor(scene: Scene, coords: LocalCoords) {
    this.scene = scene;
    this.coords = coords;
  }

  spawn(def: PickupDef): void {
    if (this.pickups.has(def.id)) return;
    const local = this.coords.toLocal(def.lat, def.lon);
    const mesh = this.createPickupMesh(def.type);
    mesh.position.set(local.x, 1.5, local.z);
    this.pickups.set(def.id, mesh);
  }

  capture(id: string): void {
    const mesh = this.pickups.get(id);
    if (!mesh) return;
    const mat = mesh.material as StandardMaterial;
    mat.emissiveColor = new Color3(1, 1, 1);
    setTimeout(() => {
      mesh.dispose();
      this.pickups.delete(id);
    }, 200);
  }

  remove(id: string): void {
    const mesh = this.pickups.get(id);
    if (mesh) {
      mesh.dispose();
      this.pickups.delete(id);
    }
  }

  clear(): void {
    for (const mesh of this.pickups.values()) mesh.dispose();
    this.pickups.clear();
  }

  update(dt: number): void {
    this.time += dt;
    for (const mesh of this.pickups.values()) {
      mesh.position.y = 1.5 + Math.sin(this.time * 3 + mesh.position.x) * 0.3;
      mesh.rotation.y += dt * 1.5;
    }
  }

  private createPickupMesh(type: PickupType): Mesh {
    const color = TYPE_COLORS[type];
    const positions = [
      0, 0.5, 0,   0.3, 0, 0,   0, -0.5, 0,   -0.3, 0, 0,
      0, 0, 0.3,   0, 0, -0.3,
    ];
    const indices = [
      0, 4, 1,  0, 1, 5,  0, 5, 3,  0, 3, 4,
      2, 1, 4,  2, 5, 1,  2, 3, 5,  2, 4, 3,
    ];
    const normals: number[] = [];
    VertexData.ComputeNormals(positions, indices, normals);

    const mesh = new Mesh('pickup_' + type, this.scene);
    const vd = new VertexData();
    vd.positions = positions;
    vd.indices = indices;
    vd.normals = normals;
    vd.applyToMesh(mesh);

    const mat = new StandardMaterial('pickupMat_' + type, this.scene);
    mat.diffuseColor = color;
    mat.emissiveColor = color.scale(0.5);
    mat.specularColor = new Color3(0.8, 0.8, 0.8);
    mesh.material = mat;
    return mesh;
  }

  dispose(): void {
    this.clear();
  }
}
