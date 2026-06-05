import { Scene, Mesh, StandardMaterial, Color3, VertexData } from '@babylonjs/core';
import { LocalCoords } from '../../map/coords.js';

export interface CityPackRoad {
  id: string;
  points: { lat: number; lon: number }[];
  width?: number;
}

export function createRoadMeshes(scene: Scene, roads: CityPackRoad[], coords: LocalCoords): Mesh {
  const positions: number[] = [];
  const indices: number[] = [];
  const normals: number[] = [];
  let idx = 0;

  for (const road of roads) {
    if (road.points.length < 2) continue;
    const width = road.width ?? 8;
    const halfWidth = width / 2;

    for (let i = 0; i < road.points.length - 1; i++) {
      const a = coords.toLocal(road.points[i].lat, road.points[i].lon);
      const b = coords.toLocal(road.points[i + 1].lat, road.points[i + 1].lon);

      const dx = b.x - a.x;
      const dz = b.z - a.z;
      const len = Math.sqrt(dx * dx + dz * dz);
      if (len < 0.001) continue;

      const perpX = (-dz / len) * halfWidth;
      const perpZ = (dx / len) * halfWidth;

      positions.push(
        a.x + perpX, 0.05, a.z + perpZ,
        a.x - perpX, 0.05, a.z - perpZ,
        b.x - perpX, 0.05, b.z - perpZ,
        a.x + perpX, 0.05, a.z + perpZ,
        b.x - perpX, 0.05, b.z - perpZ,
        b.x + perpX, 0.05, b.z + perpZ,
      );

      for (let j = 0; j < 6; j++) normals.push(0, 1, 0);
    }
  }

  if (positions.length === 0) {
    return new Mesh('emptyRoads', scene);
  }

  const mesh = new Mesh('roads', scene);
  const vd = new VertexData();
  vd.positions = positions;
  vd.indices = indices;
  vd.normals = normals;
  vd.applyToMesh(mesh);

  const mat = new StandardMaterial('roadMat', scene);
  mat.diffuseColor = new Color3(0.15, 0.15, 0.18);
  mat.specularColor = new Color3(0.05, 0.05, 0.05);
  mesh.material = mat;

  return mesh;
}
