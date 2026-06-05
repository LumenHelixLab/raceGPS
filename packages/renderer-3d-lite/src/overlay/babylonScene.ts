import {
  Engine,
  Scene,
  Vector3,
  Color4,
  HemisphericLight,
  DirectionalLight,
  GlowLayer,
  ArcRotateCamera,
  Camera,
  FreeCamera,
} from '@babylonjs/core';

export interface BabylonOverlayOptions {
  canvas: HTMLCanvasElement;
  clearColor?: Color4;
}

export interface ChaseCamOptions {
  distance?: number;
  height?: number;
  lookahead?: number;
}

export class BabylonOverlay {
  engine: Engine;
  scene: Scene;
  chaseCamera: ArcRotateCamera;
  private defaultClearColor = new Color4(0, 0, 0, 0);

  constructor(opts: BabylonOverlayOptions) {
    this.engine = new Engine(opts.canvas, true, {
      preserveDrawingBuffer: true,
      stencil: true,
      alpha: true,
    });

    this.scene = new Scene(this.engine);
    this.scene.clearColor = opts.clearColor ?? this.defaultClearColor;
    this.scene.autoClear = true;

    // Lighting: cool sky + warm directional for neon contrast
    const hemi = new HemisphericLight('hemi', new Vector3(0, 1, 0), this.scene);
    hemi.intensity = 0.4;
    hemi.diffuse.set(0.4, 0.5, 0.8);
    hemi.groundColor.set(0.1, 0.1, 0.15);

    const dir = new DirectionalLight('dir', new Vector3(0.5, -1, 0.3), this.scene);
    dir.intensity = 0.8;
    dir.diffuse.set(1.0, 0.95, 0.85);

    // Neon glow layer for pickups, checkpoints, underglow
    const gl = new GlowLayer('glow', this.scene);
    gl.intensity = 0.6;

    // Chase camera: arc-rotate style, locked behind target
    this.chaseCamera = new ArcRotateCamera(
      'chaseCam',
      -Math.PI / 2, // alpha: behind target
      Math.PI / 3,  // beta: elevation
      10,
      Vector3.Zero(),
      this.scene
    );
    this.chaseCamera.lowerRadiusLimit = 3;
    this.chaseCamera.upperRadiusLimit = 20;
    this.chaseCamera.lowerBetaLimit = 0.2;
    this.chaseCamera.upperBetaLimit = Math.PI / 2.2;
    this.chaseCamera.attachControl(opts.canvas, true);
    this.chaseCamera.inputs.clear(); // Disable mouse interaction (we drive it programmatically)

    // Resize handler
    window.addEventListener('resize', () => {
      this.engine.resize();
    });
  }

  startRenderLoop(): void {
    this.engine.runRenderLoop(() => {
      this.scene.render();
    });
  }

  stopRenderLoop(): void {
    this.engine.stopRenderLoop();
  }

  dispose(): void {
    this.scene.dispose();
    this.engine.dispose();
  }

  /**
   * Update chase camera to follow a target position + heading.
   * heading: degrees, 0=north, clockwise.
   */
  updateChaseCamera(
    x: number,
    y: number,
    z: number,
    heading: number,
    speed: number,
    opts: ChaseCamOptions = {},
  ): void {
    const distance = opts.distance ?? 5 + speed * 0.15;
    const height = opts.height ?? 2 + speed * 0.03;
    const lookahead = opts.lookahead ?? 8 + speed * 0.3;

    const headingRad = (heading * Math.PI) / 180;

    // Camera target: slightly ahead of car
    const targetX = x + Math.sin(headingRad) * lookahead;
    const targetZ = z - Math.cos(headingRad) * lookahead;

    // Camera position: behind and above
    const camX = x - Math.sin(headingRad) * distance;
    const camZ = z + Math.cos(headingRad) * distance;

    this.chaseCamera.target.set(targetX, y + 1, targetZ);
    this.chaseCamera.alpha = -headingRad - Math.PI / 2;
    this.chaseCamera.beta = Math.PI / 3 - speed * 0.003;
    this.chaseCamera.radius = distance;
    this.chaseCamera.position.set(camX, y + height, camZ);
  }
}
