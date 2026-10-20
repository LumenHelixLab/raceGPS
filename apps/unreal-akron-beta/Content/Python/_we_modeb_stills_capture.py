"""_we_modeb_stills_capture.py -- LOCAL HELPER (leading underscore: do NOT git add).

Burke Lakefront (Cleveland) Midnight photo-skyline stills S1-S3 for
docs/evidence/grokbot/world-environment-training/2026-09-27-PHOTO-SKYLINE-STILLS-PLAN.md.

Runs INSIDE the UnrealEditor GUI (rendering RHI, D3D12) via -ExecutePythonScript.
Not -game, not PIE, not a cook, not NullRHI. GlobalDefaultGameMode is never touched.
Nothing is saved: every spawned actor is transient and destroyed at the end.

Reuses existing tooling only:
  * Content/Python/verify_cleveland_map.py   -> LevelEditorSubsystem.load_level pattern
  * AClevelandEnvironmentActor::LoadAndBuild  -> BlueprintCallable; builds lake + dressing +
    BuildSkylineBackdrop() (bUsePhotoSkylineBackdrop) exactly as ClevelandShowcaseGameMode spawns it
  * AClevelandEnvironmentActor::ApplyLookMode(true) -> Midnight look MIDs + night asphalt
  * AClevelandLookDirector::ApplyVisualMode(Midnight) -> same preset path as -ClevelandPreset=Midnight
  * ClevelandShowcaseGameMode::StartSkylineIntro framing (CamLoc=pawn+(3800,2600,78),
    LookAt=pawn+(-11000,-22000,18), FOV 66, pitch clamp -4.2..0.15) -> S3
  * HighResShot + "newest PNG in ScreenShotDir" copy (ClevelandShowcaseGameMode::CaptureStill)
  * BP_DodgeCharger2024 (RaceGridManager VehicleClass) for the S3 car

World Frame A: X=east, Y=north, Z-up, 1 uu = 1 cm. Compass bearing b -> dir (sin b, cos b).
Burke EZ ribbon positions were recovered from docs/evidence/grokbot/burke-ez-ribbon/ribbon_overlay.svg
(cyan EZ polyline, 410 samples, affine fit to racing_line.json source samples: residual 0.13 m,
closed length 3272.9 m vs metrics.json 3268.99 m).

Environment overrides (all optional):
  RGPS_STILLS_OUT       output dir (default <repo>/docs/evidence/grokbot/burke-ez-ribbon/stills)
  RGPS_STILLS_RES       e.g. 1920x1080 (default)
  RGPS_STILLS_WARMUP_S  seconds to wait after build before first shot (default 45; shader/texture settle)
  RGPS_STILLS_SETTLE_S  seconds per shot after camera move (default 4; auto-exposure settle)
  RGPS_STILLS_PRESET    Midnight (default) | Twilight | Sunset
  RGPS_STILLS_SHOTS     comma list subset, e.g. S1,S3 (default all)
  RGPS_STILLS_QUIT      1 -> quit editor (no save) when done (default 0: leave editor open)
  RGPS_SKYLINE_BEARING  backdrop arc centre compass deg (default: actor default, 205)
  RGPS_SKYLINE_SPAN     backdrop arc span deg (default: actor default, 110)
  RGPS_SKYLINE_EMISSIVE backdrop emissive scale (default: actor default, 0.45)
  RGPS_S2_POSE          override S2 "x_cm,y_cm,z_above_ground_cm,ue_yaw,fov,pitch"

Recapture (2026-10-05) notes: shot poses follow the arc bearing. The engine render is
left-handed: with Frame A (X=east, Y=north), screen-right while facing +X is +Y (north).
UE yaw psi forward=(cos psi, sin psi); screen-right = yaw psi+90. Rotators are built with
keywords (unreal.Rotator positional order is roll, pitch, yaw).
"""
import json
import math
import os
import subprocess
import time

import unreal

TAG = "[WE stills]"
MAP = "/Game/Maps/Cleveland5_0KmWorld"
CHARGER_BP = "/Game/Vehicles/DodgeCharger2024/BP_DodgeCharger2024"
BACKDROP_MAT = "/Game/Materials/M_SkylineBackdrop"
BACKDROP_TEX = "/Game/Textures/T_Cleveland_SkylineNight"

PROJECT_DIR = os.path.abspath(unreal.Paths.project_dir())
REPO_DIR = os.path.abspath(os.path.join(PROJECT_DIR, "..", ".."))
OUT_DIR = os.environ.get("RGPS_STILLS_OUT") or os.path.join(
    REPO_DIR, "docs", "evidence", "grokbot", "burke-ez-ribbon", "stills")
RES = os.environ.get("RGPS_STILLS_RES", "1920x1080")
WARMUP_S = float(os.environ.get("RGPS_STILLS_WARMUP_S", "45"))
SETTLE_S = float(os.environ.get("RGPS_STILLS_SETTLE_S", "4"))
PRESET = os.environ.get("RGPS_STILLS_PRESET", "Midnight")
SHOT_FILTER = [s.strip().upper() for s in os.environ.get("RGPS_STILLS_SHOTS", "").split(",") if s.strip()]
AUTO_QUIT = os.environ.get("RGPS_STILLS_QUIT", "0") == "1"
SKY_BEARING = os.environ.get("RGPS_SKYLINE_BEARING")
SKY_SPAN = os.environ.get("RGPS_SKYLINE_SPAN")
SKY_EMISSIVE = os.environ.get("RGPS_SKYLINE_EMISSIVE")
S2_POSE = os.environ.get("RGPS_S2_POSE")

# ---------------------------------------------------------------- geometry (cm)
# Burke EZ S/F (EZ sample 0) and heading; grid slot 0 = S/F, slots step 650 cm back along the
# line, odd slots +180 cm lateral (RaceGridManager SlotSpacingCm / StaggerLateralCm).
EZ_SF = (6970.6, -8446.5)           # EZ sample 0 (source pack S/F = 6980, -8490)
EZ_SF_BEARING = 245.1               # compass; UE yaw = atan2(dy,dx) = -155.1
EZ_NORTH_STRAIGHT = (20380.0, 25770.0)   # EZ sample 246 (s~1964 m), runway 06L/24R, brg 58
EZ_NORTHMOST = (53110.0, 45490.0)        # EZ sample 294 (s~2347 m), NE corner near T5
SKYLINE_RADIUS = 260000.0
SKYLINE_CENTER_BEARING = 205.0
LAKE_SOUTH_Y = 59570.0              # water.json inner shoreline (y 596..716 m), plane Z=-20 cm
# S2 solved poses (x_cm, y_cm, z_above_ground_cm, ue_yaw, fov, pitch):
#  A (arc 205/110): best possible = EZ sample 112, yaw -9: arc only screen x[-1,-0.6], 14% of photo,
#                   nearest water 1.5 km  -> marginal.
#  B (arc 120/60):  EZ sample 246 (north straight), yaw -5: arc x[-1,-0.02] (80% of photo),
#                   lake x[0.38,1], nearest water 610 m -> recommended.
S2_POSES = {
    "A": (-68830.0, -30750.0, 3000.0, -9.0, 100.0, -2.0),
    "B": (20380.0, 25770.0, 3000.0, -5.0, 100.0, -2.0),
}


def bearing_vec(bearing_deg, dist_cm):
    r = math.radians(bearing_deg)
    return dist_cm * math.sin(r), dist_cm * math.cos(r)


def skyline_point(bearing_deg, z):
    x, y = bearing_vec(bearing_deg, SKYLINE_RADIUS)
    return unreal.Vector(x, y, z)


def rot(pitch, yaw):
    return unreal.Rotator(roll=0.0, pitch=float(pitch), yaw=float(yaw))


def rotate_compass(vx, vy, dbearing):
    """Rotate a Frame A vector by dbearing compass degrees (proper rotation)."""
    b = math.degrees(math.atan2(vx, vy)) + dbearing
    d = math.hypot(vx, vy)
    return bearing_vec(b, d)


def V(x, y, z):
    return unreal.Vector(float(x), float(y), float(z))


# ---------------------------------------------------------------- helpers
def log(msg):
    unreal.log_warning(f"{TAG} {msg}")


def editor_world():
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    return ues.get_editor_world()


def git_sha():
    try:
        return subprocess.check_output(["git", "-C", REPO_DIR, "rev-parse", "--short", "HEAD"],
                                       text=True, timeout=10).strip()
    except Exception as exc:  # noqa: BLE001
        return f"unknown({exc})"


def ground_z(world, x, y, default=0.0):
    """Line-trace straight down for ground (RaceGridManager snaps the same way)."""
    try:
        hit = unreal.SystemLibrary.line_trace_single(
            world, V(x, y, 50000), V(x, y, -50000),
            unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [],
            unreal.DrawDebugTrace.NONE, True)
        if isinstance(hit, tuple):  # (bool, HitResult) on some versions
            ok, hr = hit[0], hit[1]
        else:
            hr, ok = hit, True
        if ok and hr is not None:
            t = hr.to_tuple()
            # HitResult tuple: (blocking_hit, initial_overlap, time, distance, location, impact_point, ...)
            if t[0]:
                return float(t[5].z)
    except Exception as exc:  # noqa: BLE001
        log(f"ground trace failed at ({x:.0f},{y:.0f}): {exc}")
    return default


def look_rot(src, dst, pitch_clamp=None):
    rot = unreal.MathLibrary.find_look_at_rotation(src, dst)
    if pitch_clamp:
        rot.pitch = max(pitch_clamp[0], min(pitch_clamp[1], rot.pitch))
    return rot


def compass_of_rot(rot):
    # UE forward = (cos yaw, sin yaw) in X=east,Y=north -> compass = 90 - yaw
    return (90.0 - rot.yaw) % 360.0


def cvar(cmd):
    unreal.SystemLibrary.execute_console_command(editor_world(), cmd)


# ---------------------------------------------------------------- state
class Capture:
    def __init__(self):
        self.handle = None
        self.phase = "load"
        self.t_phase = time.time()
        self.spawned = []
        self.env = None
        self.car = None
        self.cam = None
        self.shots = []
        self.shot_idx = 0
        self.manifest = {
            "tool": "apps/unreal-akron-beta/Content/Python/_we_modeb_stills_capture.py (local helper)",
            "commit": git_sha(),
            "map": MAP,
            "mode": "UnrealEditor GUI, editor world (no -game, no PIE, no cook, no NullRHI)",
            "rhi": None,
            "preset": PRESET,
            "resolution": RES,
            "frame": "Frame A X=east Y=north Z-up cm",
            "checks": {},
            "shots": [],
            "verdict": "PENDING (human/PM grades stills; script never self-claims visual PASS)",
            "started_local": time.strftime("%Y-%m-%d %H:%M:%S %z"),
        }
        self.shot_dir_before = set()
        os.makedirs(OUT_DIR, exist_ok=True)
        self.perf_settings = None
        self.pre_existing = set()
        self.bearing = 205.0
        self.span = 110.0
        self.prev_throttle = None

    # -- tick driver
    def start(self):
        self.handle = unreal.register_slate_post_tick_callback(self.tick)
        log(f"armed; out={OUT_DIR} res={RES} warmup={WARMUP_S}s preset={PRESET}")

    def stop(self):
        if self.handle is not None:
            unreal.unregister_slate_post_tick_callback(self.handle)
            self.handle = None

    def goto(self, phase):
        self.phase = phase
        self.t_phase = time.time()

    def elapsed(self):
        return time.time() - self.t_phase

    def tick(self, _dt):
        try:
            getattr(self, "phase_" + self.phase)()
        except Exception as exc:  # noqa: BLE001
            unreal.log_error(f"{TAG} phase {self.phase} crashed: {exc}")
            self.manifest["error"] = f"{self.phase}: {exc}"
            self.goto("cleanup")

    # -- phases
    def phase_load(self):
        world = editor_world()
        cur = world.get_path_name() if world else ""
        if MAP.split("/")[-1] not in cur:
            les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
            log(f"current world {cur!r}; load_level {MAP}")
            if not les.load_level(MAP):
                raise RuntimeError(f"load_level({MAP}) failed")
        self.manifest["rhi"] = unreal.SystemLibrary.get_rendering_device_name() if hasattr(
            unreal.SystemLibrary, "get_rendering_device_name") else "see log (LogRHI)"
        self.goto("build")

    def phase_build(self):
        if self.elapsed() < 3.0:  # let the map finish registering
            return
        world = editor_world()
        eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

        # Keep the editor rendering at full rate even if the window loses focus.
        try:
            self.perf_settings = unreal.get_default_object(unreal.EditorPerformanceSettings)
            self.prev_throttle = self.perf_settings.get_editor_property("throttle_cpu_when_not_foreground")
            self.perf_settings.set_editor_property("throttle_cpu_when_not_foreground", False)
        except Exception as exc:  # noqa: BLE001
            log(f"could not disable background throttle: {exc}")

        # Assets resolve?
        mat = unreal.load_asset(BACKDROP_MAT)
        tex = unreal.load_asset(BACKDROP_TEX)
        self.manifest["checks"]["M_SkylineBackdrop_loads"] = bool(mat)
        self.manifest["checks"]["T_Cleveland_SkylineNight_loads"] = bool(tex)
        log(f"asset check mat={bool(mat)} tex={bool(tex)}")

        self.pre_existing = set(a.get_path_name() for a in eas.get_all_level_actors())
        existing = [a for a in eas.get_all_level_actors() if a.get_class().get_name() == "ClevelandEnvironmentActor"]
        self.manifest["checks"]["env_actor_already_in_level"] = len(existing)
        if existing:
            self.env = existing[0]
            log(f"using in-level EnvActor {self.env.get_name()}")
        else:
            self.env = eas.spawn_actor_from_class(unreal.ClevelandEnvironmentActor, V(0, 0, 0), unreal.Rotator(0, 0, 0), True)
            self.spawned.append(self.env)
            log("spawned transient ClevelandEnvironmentActor at origin (as ClevelandShowcaseGameMode::BeginPlay does)")
        self.env.set_editor_property("use_photo_skyline_backdrop", True)
        if SKY_BEARING:
            self.env.set_editor_property("skyline_backdrop_center_bearing_deg", float(SKY_BEARING))
        if SKY_SPAN:
            self.env.set_editor_property("skyline_backdrop_span_deg", float(SKY_SPAN))
        if SKY_EMISSIVE:
            self.env.set_editor_property("skyline_backdrop_emissive_scale", float(SKY_EMISSIVE))
        self.bearing = float(self.env.get_editor_property("skyline_backdrop_center_bearing_deg"))
        self.span = float(self.env.get_editor_property("skyline_backdrop_span_deg"))
        self.manifest["skyline_arc"] = {"center_bearing_deg": self.bearing, "span_deg": self.span,
            "emissive_scale": float(self.env.get_editor_property("skyline_backdrop_emissive_scale")),
            "mirror_u": bool(self.env.get_editor_property("skyline_backdrop_mirror_u"))}
        built = self.env.load_and_build()
        log(f"LoadAndBuild -> {built}")
        self.manifest["checks"]["load_and_build"] = bool(built)

        backdrop = self.env.get_editor_property("skyline_backdrop_mesh")
        sections = backdrop.get_num_sections() if backdrop else 0
        bmat = backdrop.get_material(0) if (backdrop and sections) else None
        if bmat and not isinstance(bmat, unreal.Material) and hasattr(bmat, "get_base_material"):
            bmat = bmat.get_base_material()  # MID (BackdropEmissiveScale) -> parent
        bmat_name = bmat.get_path_name() if bmat else None
        if bmat is not None:
            try:
                self.manifest["checks"]["backdrop_is_sky"] = bool(bmat.get_editor_property("is_sky"))
                self.manifest["checks"]["backdrop_blend_mode"] = str(bmat.get_editor_property("blend_mode"))
            except Exception:  # noqa: BLE001
                pass
        self.manifest["checks"]["backdrop_sections"] = sections
        self.manifest["checks"]["backdrop_material"] = bmat_name
        backdrop_ok = sections > 0 and bmat_name and "M_SkylineBackdrop" in bmat_name
        self.manifest["checks"]["photo_skyline_backdrop_built"] = bool(backdrop_ok)
        lake = self.env.get_editor_property("lake_mesh")
        self.manifest["checks"]["lake_sections"] = lake.get_num_sections() if lake else 0
        if not backdrop_ok:
            unreal.log_error(f"{TAG} FAIL-CLOSED: photo skyline backdrop not built (sections={sections} mat={bmat_name}); "
                             "box-skyline fallback or missing mat. Stills will be tagged FAILCTRL.")

        # Look: same path as -ClevelandPreset=<PRESET>
        mode_enum = getattr(unreal, "ClevelandVisualMode", None)
        mode = getattr(mode_enum, PRESET.upper(), None) if mode_enum else None
        if mode is not None:
            look = eas.spawn_actor_from_class(unreal.ClevelandLookDirector, V(0, 0, 0), unreal.Rotator(0, 0, 0), True)
            self.spawned.append(look)
            look.apply_visual_mode(mode)
            log(f"LookDirector.ApplyVisualMode({PRESET})")
        else:
            log("ClevelandVisualMode enum not exposed; skipping LookDirector")
        self.env.apply_look_mode(PRESET.lower() == "midnight")

        # S3 car on EZ grid slot 0 (S/F), facing direction of travel.
        cls = unreal.EditorAssetLibrary.load_blueprint_class(CHARGER_BP)
        gz = ground_z(world, EZ_SF[0], EZ_SF[1], 0.0)
        self.manifest["checks"]["ground_z_at_sf_cm"] = gz
        if cls:
            fwd = bearing_vec(EZ_SF_BEARING, 1000.0)
            yaw = math.degrees(math.atan2(fwd[1], fwd[0]))
            self.car = eas.spawn_actor_from_class(cls, V(EZ_SF[0], EZ_SF[1], gz + 40.0), rot(0.0, yaw), True)
            if self.car:
                self.spawned.append(self.car)
                log(f"car {self.car.get_name()} at S/F yaw={yaw:.1f} (compass {EZ_SF_BEARING})")
        self.manifest["checks"]["car_spawned"] = bool(self.car)

        self.cam = eas.spawn_actor_from_class(unreal.CameraActor, V(0, 0, 500), unreal.Rotator(0, 0, 0), True)
        self.spawned.append(self.cam)
        cc = self.cam.get_editor_property("camera_component")
        cc.set_editor_property("constrain_aspect_ratio", False)

        self.shots = self.build_shots(world, gz, backdrop_ok)
        if SHOT_FILTER:
            self.shots = [s for s in self.shots if s["id"].split("_")[0] in SHOT_FILTER]

        les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        try:
            les.editor_set_game_view(True)
        except Exception as exc:  # noqa: BLE001
            log(f"game view toggle failed: {exc}")
        for c in ("r.Streaming.FullyLoadUsedTextures 1", "r.ScreenPercentage 100",
                  "r.MotionBlurQuality 0", "r.SkyAtmosphere 1"):
            cvar(c)
        log(f"built; warming up {WARMUP_S}s for shader/texture/exposure settle (watch 'Compiling Shaders' toast)")
        self.goto("warmup")

    def build_shots(self, world, gz, backdrop_ok):
        tag = "" if backdrop_ok else "FAILCTRL_"
        btag = f"b{int(round(self.bearing))}"
        brg = self.bearing
        dbr = brg - 205.0  # Showcase intro framing was authored for the 205 arc
        shots = []
        # S1 skyline hero: 28.6 m behind S/F (away from the arc), eye 4 m, aimed at the arc centre
        # bearing from the camera, ~90 m up the card.
        ox, oy = bearing_vec(brg + 180.0, 2860.0)
        p = V(EZ_SF[0] + ox, EZ_SF[1] + oy, gz + 400)
        tx, ty = bearing_vec(brg, SKYLINE_RADIUS)
        tgt = V(p.x + tx, p.y + ty, 9000)
        shots.append({"id": "S1_skyline_hero", "file": f"{tag}S1_skyline_hero_{btag}", "loc": p,
                      "rot": look_rot(p, tgt, (-2.0, 3.0)), "fov": 55.0, "car": False})
        # S2 lake + skyline split (solved poses; see S2_POSES).
        if S2_POSE:
            x, y, zr, yaw, fov, pitch = [float(v) for v in S2_POSE.split(",")]
        else:
            key = "A" if abs(brg - 205.0) < 1.0 else "B"
            x, y, zr, yaw, fov, pitch = S2_POSES[key]
        p = V(x, y, ground_z(world, x, y, gz) + zr)
        shots.append({"id": "S2_lake_skyline_split", "file": f"{tag}S2_lake_skyline_split_{btag}", "loc": p,
                      "rot": rot(pitch, yaw), "fov": fov, "car": False})
        # S3 car midground: ClevelandShowcaseGameMode::StartSkylineIntro offsets, rotated by (bearing-205).
        car = V(EZ_SF[0], EZ_SF[1], gz + 40.0)
        cx, cy = rotate_compass(3800.0, 2600.0, dbr)
        lx, ly = rotate_compass(-11000.0, -22000.0, dbr)
        p = V(car.x + cx, car.y + cy, car.z + 78)
        tgt = V(car.x + lx, car.y + ly, car.z + 18)
        shots.append({"id": "S3_car_midground", "file": f"{tag}S3_car_midground_{btag}", "loc": p,
                      "rot": look_rot(p, tgt, (-4.2, 0.15)), "fov": 66.0, "car": True})
        # S3b closer car read (~16 m, low chase eye), same rotation.
        cx, cy = rotate_compass(900.0, 1400.0, dbr)
        p = V(car.x + cx, car.y + cy, car.z + 160)
        tgt = V(car.x + lx, car.y + ly, car.z + 60)
        shots.append({"id": "S3b_car_close", "file": f"{tag}S3b_car_close_{btag}", "loc": p,
                      "rot": look_rot(p, tgt, (-6.0, 0.5)), "fov": 60.0, "car": True})
        return shots

    def phase_warmup(self):
        if self.elapsed() >= WARMUP_S:
            self.shot_idx = 0
            self.goto("place")

    def phase_place(self):
        if self.shot_idx >= len(self.shots):
            self.goto("cleanup")
            return
        s = self.shots[self.shot_idx]
        self.cam.set_actor_location_and_rotation(s["loc"], s["rot"], False, True)
        self.cam.get_editor_property("camera_component").set_editor_property("field_of_view", s["fov"])
        if self.car:
            self.car.set_actor_hidden_in_game(not s["car"])
            self.car.set_is_temporarily_hidden_in_editor(not s["car"])
        les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        les.pilot_level_actor(self.cam)
        ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        ues.set_level_viewport_camera_info(s["loc"], s["rot"])
        log(f"{s['id']} cam loc=({s['loc'].x:.0f},{s['loc'].y:.0f},{s['loc'].z:.0f}) "
            f"pitch={s['rot'].pitch:.1f} yaw={s['rot'].yaw:.1f} compass={compass_of_rot(s['rot']):.1f} fov={s['fov']}")
        self.goto("settle")

    def phase_settle(self):
        if self.elapsed() < SETTLE_S:
            return
        s = self.shots[self.shot_idx]
        shot_dir = os.path.abspath(unreal.Paths.screen_shot_dir())
        self.shot_dir_before = set(self._pngs(shot_dir))
        dest = os.path.join(OUT_DIR, f"{s['file']}_{PRESET.lower()}_{self.manifest['commit']}.png")
        s["dest"] = dest
        s["shot_dir"] = shot_dir
        self.shot_dir_before |= set(self._pngs(OUT_DIR))
        cvar(f'HighResShot {RES} filename={dest.replace(os.sep, "/")}')
        log(f"{s['id']} HighResShot {RES} -> {dest}")
        self.goto("flush")

    def phase_flush(self):
        s = self.shots[self.shot_idx]
        if os.path.exists(s["dest"]):
            self._record(s, s["dest"])
            return
        # Fallback (same as CaptureStill): newest PNG that appeared in ScreenShotDir.
        new = [p for p in self._pngs(s["shot_dir"]) + self._pngs(OUT_DIR) if p not in self.shot_dir_before]
        if new and self.elapsed() > 2.5:
            newest = max(new, key=os.path.getmtime)
            import shutil
            shutil.copy2(newest, s["dest"])
            self._record(s, s["dest"], fallback_from=newest)
            return
        if self.elapsed() > 30:
            unreal.log_error(f"{TAG} {s['id']} no PNG after 30 s")
            self.manifest["shots"].append({"id": s["id"], "file": None, "error": "no PNG after 30 s"})
            self._next()

    def _record(self, s, path, fallback_from=None):
        entry = {"id": s["id"], "file": os.path.relpath(path, REPO_DIR).replace(os.sep, "/"),
                 "bytes": os.path.getsize(path),
                 "cam_loc_cm": [round(s["loc"].x, 1), round(s["loc"].y, 1), round(s["loc"].z, 1)],
                 "cam_rot": [round(s["rot"].pitch, 2), round(s["rot"].yaw, 2), round(s["rot"].roll, 2)],
                 "cam_compass_deg": round(compass_of_rot(s["rot"]), 1), "fov": s["fov"], "car_visible": s["car"]}
        if fallback_from:
            entry["copied_from"] = fallback_from
        self.manifest["shots"].append(entry)
        log(f"{s['id']} saved {path} ({entry['bytes']} bytes)")
        self._next()

    def _next(self):
        self.shot_idx += 1
        self.goto("place")

    @staticmethod
    def _pngs(d):
        try:
            out = []
            for root, _dirs, files in os.walk(d):
                out += [os.path.join(root, f) for f in files if f.lower().endswith(".png")]
            return out
        except OSError:
            return []

    def phase_cleanup(self):
        les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        try:
            les.eject_pilot_level_actor()
        except Exception:  # noqa: BLE001
            pass
        eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        for a in self.spawned:
            try:
                eas.destroy_actor(a)
            except Exception:  # noqa: BLE001
                pass
        # LookDirector/EnvActor spawn helpers (DayNightCycle, PostProcessController, ...) with
        # World->SpawnActor (non-transient): remove anything that was not in the level before.
        helper_classes = {"DayNightCycle", "PostProcessController", "BuildingMeshGenerator", "PostProcessVolume"}
        for a in eas.get_all_level_actors():
            try:
                if a.get_class().get_name() in helper_classes and a.get_path_name() not in self.pre_existing:
                    eas.destroy_actor(a)
            except Exception:  # noqa: BLE001
                pass
        log("cleanup done. Level may still be marked dirty (LookDirector hides level lights): "
            "DO NOT SAVE the map; answer 'Don't Save' on exit.")
        if self.perf_settings is not None and self.prev_throttle is not None:
            self.perf_settings.set_editor_property("throttle_cpu_when_not_foreground", self.prev_throttle)
        self.manifest["finished_local"] = time.strftime("%Y-%m-%d %H:%M:%S %z")
        mpath = os.path.join(OUT_DIR, f"capture_manifest_{PRESET.lower()}_b{int(round(self.bearing))}_{self.manifest['commit']}.json")
        with open(mpath, "w", encoding="utf-8") as fh:
            json.dump(self.manifest, fh, indent=2)
        log(f"DONE shots={len([s for s in self.manifest['shots'] if s.get('file')])}/{len(self.shots)} manifest={mpath}")
        log("Grep the editor log for 'photo skyline backdrop built' vs 'M_SkylineBackdrop missing'.")
        self.stop()
        if AUTO_QUIT:
            unreal.SystemLibrary.quit_editor()


_CAPTURE = Capture()
_CAPTURE.start()
