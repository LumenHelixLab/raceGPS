/**
 * Street-Level Arcade Renderer — Clean Rewrite
 *
 * True chase-cam driving with satellite ground, GLB cars, and 60fps physics.
 */

import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { SatelliteGround } from './satellite-ground.js';

// ── Types ────────────────────────────────────────────────────

export interface CityPackRoad {
  id: string;
  points: { lat: number; lon: number }[];
  width?: number;
}

export interface CityPackBuilding {
  id: string;
  rings: { lat: number; lon: number }[][];
  height: number;
  roofType?: 'flat' | 'gabled' | 'hipped' | 'pyramidal';
}

export interface VehicleState {
  x: number;
  y: number;
  z: number;
  heading: number; // degrees, 0=north, clockwise
  speed: number;   // m/s
}

// ── Coordinate Conversion ────────────────────────────────────

const METERS_PER_DEG_LAT = 111320;

export class LocalCoords {
  originLat: number;
  originLon: number;
  cosOriginLat: number;

  constructor(originLat: number, originLon: number) {
    this.originLat = originLat;
    this.originLon = originLon;
    this.cosOriginLat = Math.cos((originLat * Math.PI) / 180);
  }

  toLocal(lat: number, lon: number, altitude = 0): { x: number; y: number; z: number } {
    const dLat = lat - this.originLat;
    const dLon = lon - this.originLon;
    return {
      x: dLon * METERS_PER_DEG_LAT * this.cosOriginLat,
      y: altitude,
      z: -dLat * METERS_PER_DEG_LAT,
    };
  }

  toLatLon(x: number, z: number): { lat: number; lon: number } {
    return {
      lat: this.originLat + (-z / METERS_PER_DEG_LAT),
      lon: this.originLon + (x / (METERS_PER_DEG_LAT * this.cosOriginLat)),
    };
  }
}

// ── Environment ──────────────────────────────────────────────

function createRoadMesh(roads: CityPackRoad[], coords: LocalCoords): THREE.Mesh {
  const positions: number[] = [];
  const normals: number[] = [];

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

  const geom = new THREE.BufferGeometry();
  geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geom.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));

  const mat = new THREE.MeshStandardMaterial({
    color: 0x33333a,
    roughness: 0.9,
    metalness: 0.05,
  });

  return new THREE.Mesh(geom, mat);
}

function createRoadMarkings(roads: CityPackRoad[], coords: LocalCoords): THREE.Mesh {
  const positions: number[] = [];

  for (const road of roads) {
    if (road.points.length < 2) continue;
    for (let i = 0; i < road.points.length - 1; i++) {
      const a = coords.toLocal(road.points[i].lat, road.points[i].lon);
      const b = coords.toLocal(road.points[i + 1].lat, road.points[i + 1].lon);
      const dx = b.x - a.x;
      const dz = b.z - a.z;
      const len = Math.sqrt(dx * dx + dz * dz);
      if (len < 2) continue;

      const dashLen = 3, gapLen = 3, totalDash = dashLen + gapLen;
      const numDashes = Math.floor(len / totalDash);
      const nx = dx / len, nz = dz / len;

      for (let d = 0; d < numDashes; d++) {
        const t0 = (d * totalDash) / len;
        const t1 = (d * totalDash + dashLen) / len;
        const p0 = { x: a.x + nx * t0 * len, z: a.z + nz * t0 * len };
        const p1 = { x: a.x + nx * t1 * len, z: a.z + nz * t1 * len };
        const markWidth = 0.15;
        const perpX = -nz * markWidth;
        const perpZ = nx * markWidth;

        positions.push(
          p0.x + perpX, 0.06, p0.z + perpZ,
          p0.x - perpX, 0.06, p0.z - perpZ,
          p1.x - perpX, 0.06, p1.z - perpZ,
          p0.x + perpX, 0.06, p0.z + perpZ,
          p1.x - perpX, 0.06, p1.z - perpZ,
          p1.x + perpX, 0.06, p1.z + perpZ,
        );
      }
    }
  }

  const geom = new THREE.BufferGeometry();
  geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  return new THREE.Mesh(geom, new THREE.MeshBasicMaterial({ color: 0xdddddd }));
}

function createBuildingMeshes(buildings: CityPackBuilding[], coords: LocalCoords): THREE.Group {
  const group = new THREE.Group();
  const bodyMat = new THREE.MeshStandardMaterial({ color: 0x5a5a65, roughness: 0.85 });
  const windowMat = new THREE.MeshStandardMaterial({ color: 0xffee88, emissive: 0xffaa44, emissiveIntensity: 0.4 });

  let count = 0;
  for (const b of buildings) {
    if (!b.rings?.length) continue;
    const ring = b.rings[0];
    if (ring.length < 3) continue;

    let minX = Infinity, maxX = -Infinity, minZ = Infinity, maxZ = -Infinity;
    for (const p of ring) {
      const local = coords.toLocal(p.lat, p.lon);
      minX = Math.min(minX, local.x);
      maxX = Math.max(maxX, local.x);
      minZ = Math.min(minZ, local.z);
      maxZ = Math.max(maxZ, local.z);
    }
    const cx = (minX + maxX) / 2;
    const cz = (minZ + maxZ) / 2;
    const w = Math.max(0.5, maxX - minX);
    const d = Math.max(0.5, maxZ - minZ);
    const h = Math.max(3, b.height || 12);
    if (count > 400) break;
    count++;

    const body = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), bodyMat);
    body.position.set(cx, h / 2, cz);
    body.castShadow = true;
    body.receiveShadow = true;
    group.add(body);

    if (h > 6) {
      const winGeom = new THREE.PlaneGeometry(w * 0.5, h * 0.3);
      const winFront = new THREE.Mesh(winGeom, windowMat);
      winFront.position.set(cx, h * 0.55, cz - d / 2 - 0.05);
      group.add(winFront);
      const winBack = new THREE.Mesh(winGeom, windowMat);
      winBack.position.set(cx, h * 0.55, cz + d / 2 + 0.05);
      winBack.rotation.y = Math.PI;
      group.add(winBack);
    }
  }
  return group;
}

// ── Street Renderer ──────────────────────────────────────────

export class StreetRenderer {
  private renderer: THREE.WebGLRenderer;
  private scene: THREE.Scene;
  private camera: THREE.PerspectiveCamera;
  private canvasEl: HTMLCanvasElement;
  private car: THREE.Group = new THREE.Group();
  private wheels: THREE.Object3D[] = [];
  private carLoaded = false;
  private running = false;
  private animationId = 0;

  // Interpolated state for smooth 60fps rendering
  private displayState: VehicleState = { x: 0, y: 0, z: 0, heading: 0, speed: 0 };
  private targetState: VehicleState = { x: 0, y: 0, z: 0, heading: 0, speed: 0 };
  private wheelAccum = 0;

  private satellite?: SatelliteGround;

  constructor(canvas: HTMLCanvasElement) {
    this.canvasEl = canvas;
    const w = window.innerWidth;
    const h = window.innerHeight;
    canvas.width = w;
    canvas.height = h;

    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    this.renderer.setSize(w, h);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;

    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x080810);
    this.scene.fog = new THREE.Fog(0x080810, 80, 400);

    this.camera = new THREE.PerspectiveCamera(65, w / h, 0.1, 2000);

    // Brighter lighting
    const hemi = new THREE.HemisphereLight(0x6688ff, 0x222233, 0.6);
    this.scene.add(hemi);

    const dir = new THREE.DirectionalLight(0xffeedd, 1.0);
    dir.position.set(60, 120, 40);
    dir.castShadow = true;
    dir.shadow.mapSize.set(2048, 2048);
    dir.shadow.camera.near = 1;
    dir.shadow.camera.far = 400;
    dir.shadow.camera.left = -120;
    dir.shadow.camera.right = 120;
    dir.shadow.camera.top = 120;
    dir.shadow.camera.bottom = -120;
    this.scene.add(dir);

    // Ambient fill
    this.scene.add(new THREE.AmbientLight(0x404060, 0.3));

    this.scene.add(this.car);
    window.addEventListener('resize', () => this.onResize());
  }

  private onResize(): void {
    const w = window.innerWidth;
    const h = window.innerHeight;
    this.canvasEl.width = w;
    this.canvasEl.height = h;
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h);
  }

  // ── Car Loading ────────────────────────────────────────────

  switchCarModel(url: string): Promise<void> {
    if (this.carLoaded) {
      this.scene.remove(this.car);
      this.car = new THREE.Group();
      this.wheels = [];
      this.carLoaded = false;
    }
    return this.loadCarModel(url);
  }

  loadCarModel(url: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const loader = new GLTFLoader();
      loader.load(
        url,
        (gltf) => {
          this.scene.remove(this.car);
          const model = gltf.scene;

          // Apply Kenney colormap texture manually
          if (url.includes('kenney')) {
            const texPath = url.replace(/\/[^/]+$/, '') + '/Textures/colormap.png';
            new THREE.TextureLoader().load(
              texPath,
              (tex) => {
                tex.colorSpace = THREE.SRGBColorSpace;
                tex.magFilter = THREE.NearestFilter;
                tex.minFilter = THREE.NearestFilter;
                model.traverse((c) => {
                  if (c instanceof THREE.Mesh && c.material) {
                    const mats = Array.isArray(c.material) ? c.material : [c.material];
                    mats.forEach((m: THREE.Material) => {
                      if ((m as THREE.MeshStandardMaterial).map !== undefined) {
                        (m as THREE.MeshStandardMaterial).map = tex;
                        m.needsUpdate = true;
                      }
                    });
                  }
                });
              },
              undefined,
              (err) => console.warn('[StreetRenderer] Texture load failed:', err),
            );
          }

          // Find wheels by name
          this.wheels = [];
          model.traverse((child) => {
            if (child.name.toLowerCase().includes('wheel')) {
              this.wheels.push(child);
            }
          });

          // Scale to real size
          const box = new THREE.Box3().setFromObject(model);
          const size = new THREE.Vector3();
          box.getSize(size);
          const targetLen = 4.0;
          const scale = targetLen / size.z;
          model.scale.setScalar(scale);

          // Lift to ground
          const scaledBox = new THREE.Box3().setFromObject(model);
          model.position.y = -scaledBox.min.y;

          console.log('[StreetRenderer] Car loaded:', url, 'scale:', scale.toFixed(2), 'wheels:', this.wheels.length);

          this.car = model;
          this.carLoaded = true;
          this.scene.add(model);

          // Headlights (front of car is +Z in Kenney model)
          const beamL = new THREE.SpotLight(0xffffee, 6, 60, 0.5, 0.3, 1);
          beamL.position.set(-0.6, 0.7, 1.6);
          beamL.target.position.set(-0.6, 0, 15);
          this.car.add(beamL);
          this.car.add(beamL.target);

          const beamR = new THREE.SpotLight(0xffffee, 6, 60, 0.5, 0.3, 1);
          beamR.position.set(0.6, 0.7, 1.6);
          beamR.target.position.set(0.6, 0, 15);
          this.car.add(beamR);
          this.car.add(beamR.target);

          // Underglow
          const glow = new THREE.PointLight(0x00aaff, 1.0, 5);
          glow.position.set(0, 0.05, 0);
          this.car.add(glow);

          resolve();
        },
        undefined,
        (err) => reject(err),
      );
    });
  }

  // ── City Loading ───────────────────────────────────────────

  loadCity(roads: CityPackRoad[], buildings: CityPackBuilding[], originLat: number, originLon: number): LocalCoords {
    const coords = new LocalCoords(originLat, originLon);

    // Fallback ground plane (visible immediately, satellite tiles load over it)
    const groundGeom = new THREE.PlaneGeometry(4000, 4000);
    const groundMat = new THREE.MeshStandardMaterial({
      color: 0x1a2a1a,
      roughness: 1.0,
      metalness: 0.0,
    });
    const ground = new THREE.Mesh(groundGeom, groundMat);
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -0.05;
    ground.receiveShadow = true;
    this.scene.add(ground);

    // Satellite ground tiles
    this.satellite = new SatelliteGround(this.scene, coords, 17);

    // Roads and buildings
    this.scene.add(createRoadMesh(roads, coords));
    this.scene.add(createRoadMarkings(roads, coords));
    this.scene.add(createBuildingMeshes(buildings, coords));

    return coords;
  }

  // ── Update ─────────────────────────────────────────────────

  /** Call this from your physics tick (e.g. 20Hz) with the new state. */
  setTargetState(state: VehicleState): void {
    this.targetState = { ...state };

    // Smooth heading wrap-around
    let dh = this.targetState.heading - this.displayState.heading;
    while (dh > 180) dh -= 360;
    while (dh < -180) dh += 360;
    this.targetState.heading = this.displayState.heading + dh;
  }

  private updateVisuals(dt: number): void {
    // Smoothly interpolate display state toward target for 60fps smoothness
    const t = 1 - Math.exp(-dt * 15); // spring-like smoothing
    this.displayState.x += (this.targetState.x - this.displayState.x) * t;
    this.displayState.y += (this.targetState.y - this.displayState.y) * t;
    this.displayState.z += (this.targetState.z - this.displayState.z) * t;
    this.displayState.heading += (this.targetState.heading - this.displayState.heading) * t;
    this.displayState.speed = this.targetState.speed;

    if (!this.carLoaded) return;

    // Kenney car front is +Z. Our heading 0 = north = -Z.
    // Add PI so car front points in movement direction.
    const headingRad = (this.displayState.heading * Math.PI) / 180;
    this.car.position.set(this.displayState.x, this.displayState.y, this.displayState.z);
    // Kenney model front is +Z. Heading 0 = north = world -Z.
    // rotation.y = PI makes +Z face -Z (north). 
    // rotation.y = PI - headingRad correctly rotates for all headings.
    this.car.rotation.y = Math.PI - headingRad;

    // Spin wheels
    const wheelSpeed = (this.displayState.speed * dt) / 0.34;
    this.wheelAccum += wheelSpeed;
    for (const w of this.wheels) {
      w.rotation.x = this.wheelAccum;
    }

    // Update satellite tiles as car moves
    this.satellite?.update(this.displayState.x, this.displayState.z);
  }

  private updateCamera(): void {
    const headingRad = (this.displayState.heading * Math.PI) / 180;
    const speed = this.displayState.speed;

    // Chase cam: behind and above the car
    const distance = 4.5 + speed * 0.12;
    const height = 1.6 + speed * 0.025;

    // Camera is behind the car (opposite to heading)
    const camX = this.displayState.x - Math.sin(headingRad) * distance;
    const camZ = this.displayState.z + Math.cos(headingRad) * distance;

    // Look at point slightly ahead of car
    const lookAhead = 12 + speed * 0.4;
    const lookX = this.displayState.x + Math.sin(headingRad) * lookAhead;
    const lookZ = this.displayState.z - Math.cos(headingRad) * lookAhead;

    this.camera.position.set(camX, this.displayState.y + height, camZ);
    this.camera.lookAt(lookX, this.displayState.y + 1.0, lookZ);

    // Dynamic FOV
    const targetFov = 65 + Math.min(speed * 0.4, 15);
    this.camera.fov += (targetFov - this.camera.fov) * 0.05;
    this.camera.updateProjectionMatrix();
  }

  // ── Render Loop ────────────────────────────────────────────

  private lastTime = 0;

  start(): void {
    if (this.running) return;
    this.running = true;
    this.lastTime = performance.now();

    const loop = (now: number) => {
      if (!this.running) return;
      this.animationId = requestAnimationFrame(loop);

      const dt = Math.min((now - this.lastTime) / 1000, 0.1); // cap at 100ms
      this.lastTime = now;

      this.updateVisuals(dt);
      this.updateCamera();
      this.renderer.render(this.scene, this.camera);
    };

    this.animationId = requestAnimationFrame(loop);
  }

  stop(): void {
    this.running = false;
    cancelAnimationFrame(this.animationId);
    this.renderer.dispose();
  }
}
