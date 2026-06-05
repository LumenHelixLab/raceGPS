import {
  Scene,
  Mesh,
  StandardMaterial,
  Color3,
  VertexData,
  TransformNode,
} from '@babylonjs/core';
import { LocalCoords } from '../../map/coords.js';

export interface PlayerMarkerState {
  playerId: string;
  lat: number;
  lon: number;
  heading: number;
  displayName?: string;
}

export class PlayerMarkers {
  private scene: Scene;
  private coords: LocalCoords;
  private markers = new Map<string, TransformNode>();

  constructor(scene: Scene, coords: LocalCoords) {
    this.scene = scene;
    this.coords = coords;
  }

  upsert(state: PlayerMarkerState): void {
    let node = this.markers.get(state.playerId);
    if (!node) {
      node = new TransformNode('player_' + state.playerId, this.scene);
      const arrow = this.createArrowMesh(state.playerId === 'me' ? new Color3(0, 1, 0.5) : new Color3(1, 0.5, 0));
      arrow.parent = node;
      arrow.position.y = 0.5;
      this.markers.set(state.playerId, node);
    }

    const local = this.coords.toLocal(state.lat, state.lon);
    node.position.set(local.x, 0, local.z);
    node.rotation.y = Math.PI - (state.heading * Math.PI) / 180;
  }

  remove(playerId: string): void {
    const node = this.markers.get(playerId);
    if (node) {
      node.dispose();
      this.markers.delete(playerId);
    }
  }

  clear(): void {
    for (const node of this.markers.values()) node.dispose();
    this.markers.clear();
  }

  private createArrowMesh(color: Color3): Mesh {
    const positions = [
      0, 0, 0.5,    // nose
      -0.3, 0, -0.3, // left wing
      0.3, 0, -0.3,  // right wing
      0, 0.1, 0,     // top
    ];
    const indices = [
      0, 2, 3,  0, 3, 1,
      1, 3, 2,  1, 2, 0,
    ];
    const normals: number[] = [];
    VertexData.ComputeNormals(positions, indices, normals);

    const mesh = new Mesh('arrow', this.scene);
    const vd = new VertexData();
    vd.positions = positions;
    vd.indices = indices;
    vd.normals = normals;
    vd.applyToMesh(mesh);

    const mat = new StandardMaterial('arrowMat', this.scene);
    mat.diffuseColor = color;
    mat.emissiveColor = color.scale(0.6);
    mesh.material = mat;
    return mesh;
  }

  dispose(): void {
    this.clear();
  }
}
