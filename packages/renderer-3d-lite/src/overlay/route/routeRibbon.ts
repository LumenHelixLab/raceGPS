import {
  Scene,
  Mesh,
  StandardMaterial,
  Color3,
  VertexData,
  Vector3,
  GlowLayer,
} from '@babylonjs/core';
import { LocalCoords } from '../../map/coords.js';

export interface MapPoint {
  lat: number;
  lon: number;
}

export class RouteRibbon {
  private scene: Scene;
  private mesh?: Mesh;
  private coords: LocalCoords;

  constructor(scene: Scene, coords: LocalCoords) {
    this.scene = scene;
    this.coords = coords;
  }

  draw(points: MapPoint[]): void {
    this.clear();
    if (points.length < 2) return;

    const localPoints = points.map((p) => {
      const local = this.coords.toLocal(p.lat, p.lon);
      return new Vector3(local.x, 0.3, local.z);
    });

    // Build a tube/ribbon along the path
    const width = 3;
    const halfWidth = width / 2;
    const positions: number[] = [];
    const indices: number[] = [];
    const normals: number[] = [];
    let idx = 0;

    for (let i = 0; i < localPoints.length - 1; i++) {
      const a = localPoints[i];
      const b = localPoints[i + 1];
      const dir = b.subtract(a).normalize();
      const perp = new Vector3(-dir.z, 0, dir.x).scale(halfWidth);

      const v0 = a.add(perp);
      const v1 = a.subtract(perp);
      const v2 = b.subtract(perp);
      const v3 = b.add(perp);

      positions.push(
        v0.x, v0.y, v0.z,
        v1.x, v1.y, v1.z,
        v2.x, v2.y, v2.z,
        v3.x, v3.y, v3.z,
      );
      indices.push(
        idx, idx + 1, idx + 2,
        idx, idx + 2, idx + 3,
      );
      idx += 4;
    }

    VertexData.ComputeNormals(positions, indices, normals);

    this.mesh = new Mesh('routeRibbon', this.scene);
    const vd = new VertexData();
    vd.positions = positions;
    vd.indices = indices;
    vd.normals = normals;
    vd.applyToMesh(this.mesh);

    const mat = new StandardMaterial('routeMat', this.scene);
    mat.diffuseColor = new Color3(0, 0.8, 1);
    mat.emissiveColor = new Color3(0, 0.4, 0.6);
    mat.specularColor = new Color3(0, 0, 0);
    this.mesh.material = mat;
  }

  clear(): void {
    if (this.mesh) {
      this.mesh.dispose();
      this.mesh = undefined;
    }
  }

  dispose(): void {
    this.clear();
  }
}
