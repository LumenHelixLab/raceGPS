import { Scene, Mesh, StandardMaterial, Color3, VertexData, Vector3 } from '@babylonjs/core';
import { LocalCoords } from '../../map/coords.js';

export interface CityPackBuilding {
  id: string;
  rings: { lat: number; lon: number }[][];
  height: number;
}

export function createBuildingMeshes(scene: Scene, buildings: CityPackBuilding[], coords: LocalCoords): Mesh {
  const positions: number[] = [];
  const indices: number[] = [];
  const normals: number[] = [];
  let idx = 0;

  let count = 0;
  for (const b of buildings) {
    if (!b.rings?.length) continue;
    const ring = b.rings[0];
    if (ring.length < 3) continue;
    if (count > 400) break;
    count++;

    const h = Math.max(3, b.height || 12);

    // Convert ring to local XY coordinates
    const pts = ring.map((p) => coords.toLocal(p.lat, p.lon));

    // Compute center for this building
    let cx = 0, cz = 0;
    for (const p of pts) { cx += p.x; cz += p.z; }
    cx /= pts.length;
    cz /= pts.length;

    // Simplified: use bounding box extrusion instead of exact polygon
    let minX = Infinity, maxX = -Infinity, minZ = Infinity, maxZ = -Infinity;
    for (const p of pts) {
      minX = Math.min(minX, p.x);
      maxX = Math.max(maxX, p.x);
      minZ = Math.min(minZ, p.z);
      maxZ = Math.max(maxZ, p.z);
    }

    const w = Math.max(0.5, maxX - minX);
    const d = Math.max(0.5, maxZ - minZ);

    // Box vertices: bottom face then top face
    // 0: (-w/2, 0, -d/2)   1: (w/2, 0, -d/2)
    // 2: (w/2, 0, d/2)     3: (-w/2, 0, d/2)
    // 4: (-w/2, h, -d/2)   5: (w/2, h, -d/2)
    // 6: (w/2, h, d/2)     7: (-w/2, h, d/2)
    const basePositions = [
      cx - w/2, 0, cz - d/2,
      cx + w/2, 0, cz - d/2,
      cx + w/2, 0, cz + d/2,
      cx - w/2, 0, cz + d/2,
      cx - w/2, h, cz - d/2,
      cx + w/2, h, cz - d/2,
      cx + w/2, h, cz + d/2,
      cx - w/2, h, cz + d/2,
    ];

    const baseIndices = [
      // Bottom
      0, 2, 1, 0, 3, 2,
      // Top
      4, 5, 6, 4, 6, 7,
      // Front
      0, 1, 5, 0, 5, 4,
      // Back
      2, 3, 7, 2, 7, 6,
      // Left
      3, 0, 4, 3, 4, 7,
      // Right
      1, 2, 6, 1, 6, 5,
    ];

    for (const p of basePositions) positions.push(p);
    for (const i of baseIndices) indices.push(i + idx);
    idx += 8;
  }

  if (positions.length === 0) {
    return new Mesh('emptyBuildings', scene);
  }

  // Compute normals
  VertexData.ComputeNormals(positions, indices, normals);

  const mesh = new Mesh('buildings', scene);
  const vd = new VertexData();
  vd.positions = positions;
  vd.indices = indices;
  vd.normals = normals;
  vd.applyToMesh(mesh);

  const mat = new StandardMaterial('bldgMat', scene);
  mat.diffuseColor = new Color3(0.2, 0.2, 0.25);
  mat.specularColor = new Color3(0.05, 0.05, 0.05);
  mesh.material = mat;

  return mesh;
}
