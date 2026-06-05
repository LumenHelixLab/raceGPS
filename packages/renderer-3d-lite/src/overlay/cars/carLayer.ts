import {
  Scene,
  Vector3,
  Mesh,
  AbstractMesh,
  TransformNode,
  SceneLoader,
  StandardMaterial,
  Texture,
  Color3,
  SpotLight,
  PointLight,
} from '@babylonjs/core';
import '@babylonjs/loaders/glTF';

export interface VehicleState {
  x: number;
  y: number;
  z: number;
  heading: number; // degrees, 0=north, clockwise
  speed: number;   // m/s, signed: positive=forward, negative=reverse
}

export class CarLayer {
  private scene: Scene;
  private carRoot: TransformNode | null = null;
  private wheels: Mesh[] = [];
  private wheelAccum = 0;
  private carLoaded = false;
  private currentUrl = '';

  constructor(scene: Scene) {
    this.scene = scene;
  }

  async loadCar(url: string): Promise<void> {
    if (this.carLoaded && this.currentUrl === url) return;
    this.currentUrl = url;

    // Remove old car
    if (this.carRoot) {
      this.carRoot.dispose();
      this.carRoot = null;
      this.wheels = [];
    }

    try {
      const result = await SceneLoader.ImportMeshAsync(
        '',
        url.substring(0, url.lastIndexOf('/') + 1),
        url.substring(url.lastIndexOf('/') + 1),
        this.scene,
      );

      const root = new TransformNode('carRoot', this.scene);

      // Parent all loaded meshes to our root
      for (const mesh of result.meshes) {
        if ((mesh as AbstractMesh).parent === null) {
          mesh.parent = root;
        }
      }

      // Apply Kenney colormap if needed
      if (url.includes('kenney')) {
        const texPath = url.replace(/\/[^/]+$/, '') + '/Textures/colormap.png';
        const tex = new Texture(texPath, this.scene);
        tex.wrapU = Texture.WRAP_ADDRESSMODE;
        tex.wrapV = Texture.WRAP_ADDRESSMODE;
        tex.hasAlpha = false;

        for (const mesh of result.meshes) {
          if (mesh.material && (mesh.material as StandardMaterial).diffuseTexture === null) {
            (mesh.material as StandardMaterial).diffuseTexture = tex;
          }
        }
      }

      // Scale to ~4 meters real-world length
      let minZ = Infinity;
      let maxZ = -Infinity;
      for (const mesh of result.meshes) {
        if (!mesh.getBoundingInfo()) continue;
        const b = mesh.getBoundingInfo().boundingBox;
        minZ = Math.min(minZ, b.minimumWorld.z);
        maxZ = Math.max(maxZ, b.maximumWorld.z);
      }
      const modelLen = maxZ - minZ || 1;
      const scale = 4.0 / modelLen;
      root.scaling.setAll(scale);

      // Find wheels by name
      this.wheels = [];
      for (const mesh of result.meshes) {
        const name = mesh.name.toLowerCase();
        if (name.includes('wheel') && mesh instanceof Mesh) {
          this.wheels.push(mesh);
        }
      }

      // Headlights
      const beamL = new SpotLight(
        'headlightL',
        new Vector3(-0.6, 0.7, 1.6),
        new Vector3(0, -0.1, 1),
        Math.PI / 3,
        20,
        this.scene,
      );
      beamL.intensity = 8;
      beamL.diffuse = new Color3(1, 0.97, 0.93);
      beamL.parent = root;

      const beamR = new SpotLight(
        'headlightR',
        new Vector3(0.6, 0.7, 1.6),
        new Vector3(0, -0.1, 1),
        Math.PI / 3,
        20,
        this.scene,
      );
      beamR.intensity = 8;
      beamR.diffuse = new Color3(1, 0.97, 0.93);
      beamR.parent = root;

      // Underglow
      const glow = new PointLight('underglow', new Vector3(0, 0.1, 0), this.scene);
      glow.intensity = 2;
      glow.diffuse = new Color3(0.0, 0.6, 1.0);
      glow.range = 6;
      glow.parent = root;

      this.carRoot = root;
      this.carLoaded = true;
      console.log('[CarLayer] Car loaded:', url, 'wheels:', this.wheels.length);
    } catch (err) {
      console.error('[CarLayer] Failed to load car:', url, err);
      throw err;
    }
  }

  update(state: VehicleState, dt: number): void {
    if (!this.carRoot || !this.carLoaded) return;

    // Position
    this.carRoot.position.set(state.x, state.y, state.z);

    // Rotation: heading 0=north=-Z. Kenney model front=+Z.
    // rotation.y = PI - headingRad makes +Z face north.
    const headingRad = (state.heading * Math.PI) / 180;
    this.carRoot.rotation.y = Math.PI - headingRad;

    // Wheel spin
    const wheelCircumference = 2 * Math.PI * 0.34;
    const rotDelta = (state.speed * dt) / wheelCircumference * 2 * Math.PI;
    this.wheelAccum += rotDelta;
    for (const wheel of this.wheels) {
      wheel.rotation.x = this.wheelAccum;
    }
  }

  dispose(): void {
    if (this.carRoot) {
      this.carRoot.dispose();
      this.carRoot = null;
    }
    this.wheels = [];
    this.carLoaded = false;
  }
}
