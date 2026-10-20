"""_va_body_mi_verify.py -- LOCAL HELPER (do NOT git add).

VA body MI slice verify (NOT Mode B visual PASS).
Re-run after create_bodypaint_skeletal_safe.py.
"""
import json
import math
import os
import shutil
import subprocess
import time

import unreal

TAG = "[VA body-mi verify]"
CHARGER_BP = "/Game/Vehicles/DodgeCharger2024/BP_DodgeCharger2024"
MASTER_PATH = "/Game/Materials/M_BodyPaint_SkeletalSafe"
MI_PATH = "/Game/Materials/MI_ChargerBody_SkeletalSafe"

PROJECT_DIR = os.path.abspath(unreal.Paths.project_dir())
REPO_DIR = os.path.abspath(os.path.join(PROJECT_DIR, "..", ".."))
OUT_DIR = os.environ.get("RGPS_STILLS_OUT") or os.path.join(
    REPO_DIR, "docs", "evidence", "grokbot", "burke-ez-ribbon", "stills", "va-body-mi-2026-10-05")
RES = os.environ.get("RGPS_STILLS_RES", "1920x1080")
WARMUP_S = float(os.environ.get("RGPS_STILLS_WARMUP_S", "35"))
SETTLE_S = float(os.environ.get("RGPS_STILLS_SETTLE_S", "6"))
AUTO_QUIT = os.environ.get("RGPS_STILLS_QUIT", "0") == "1"
EZ_SF = (6970.6, -8446.5)
EZ_SF_BEARING = 245.1


def log(msg):
    unreal.log_warning(f"{TAG} {msg}")


def editor_world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def cvar(cmd):
    unreal.SystemLibrary.execute_console_command(editor_world(), cmd)


def git_sha():
    try:
        return subprocess.check_output(
            ["git", "-C", REPO_DIR, "rev-parse", "--short", "HEAD"], text=True, timeout=10
        ).strip()
    except Exception as exc:
        return f"unknown({exc})"


def V(x, y, z):
    return unreal.Vector(float(x), float(y), float(z))


def rot(pitch, yaw):
    return unreal.Rotator(roll=0.0, pitch=float(pitch), yaw=float(yaw))


def bearing_vec(bearing_deg, dist_cm):
    r = math.radians(bearing_deg)
    return dist_cm * math.sin(r), dist_cm * math.cos(r)


def ground_z(world, x, y, default=0.0):
    try:
        hit = unreal.SystemLibrary.line_trace_single(
            world, V(x, y, 50000), V(x, y, -50000),
            unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [],
            unreal.DrawDebugTrace.NONE, True)
        if isinstance(hit, tuple):
            ok, hr = hit[0], hit[1]
        else:
            hr, ok = hit, True
        if ok and hr is not None:
            t = hr.to_tuple()
            if t[0]:
                return float(t[5].z)
    except Exception as exc:
        log(f"ground trace failed: {exc}")
    return default


def pngs(d):
    out = []
    try:
        for root, _dirs, files in os.walk(d):
            out += [os.path.join(root, f) for f in files if f.lower().endswith(".png")]
    except OSError:
        pass
    return out


class Runner:
    def __init__(self):
        self.handle = None
        self.phase = "init"
        self.t0 = time.time()
        self.spawned = []
        self.car = None
        self.cam = None
        self.checks = {"commit": git_sha()}
        self.dest = None
        self.shot_dir = None
        self.before = set()
        self.prev_throttle = None

    def elapsed(self):
        return time.time() - self.t0

    def goto(self, phase):
        self.phase = phase
        self.t0 = time.time()
        log(f"phase -> {phase}")

    def tick(self, _dt):
        try:
            if self.phase == "init":
                self.do_init()
            elif self.phase == "warmup":
                if self.elapsed() >= WARMUP_S:
                    self.do_shot()
            elif self.phase == "flush":
                self.do_flush()
            elif self.phase == "done":
                return False
        except Exception as exc:
            unreal.log_error(f"{TAG} tick exception: {exc}")
            self.finish(ok=False)
            return False
        return True

    def do_init(self):
        os.makedirs(OUT_DIR, exist_ok=True)
        # Keep editor rendering when not foreground (WE stills do this)
        try:
            perf = unreal.SystemLibrary.get_engine_subsystem(unreal.EditorPerformanceSettings) if False else None
        except Exception:
            perf = None
        try:
            import unreal as u
            # EditorPerformanceSettings via config object
            settings = unreal.get_default_object(unreal.EditorPerformanceSettings) if hasattr(unreal, "EditorPerformanceSettings") else None
            if settings is None:
                try:
                    settings = unreal.load_object(None, "/Script/UnrealEd.Default__EditorPerformanceSettings")
                except Exception:
                    settings = None
            if settings:
                self.prev_throttle = settings.get_editor_property("throttle_cpu_when_not_foreground")
                settings.set_editor_property("throttle_cpu_when_not_foreground", False)
                log(f"throttle_cpu_when_not_foreground {self.prev_throttle} -> False")
        except Exception as exc:
            log(f"perf settings skip: {exc}")

        master = unreal.EditorAssetLibrary.load_asset(MASTER_PATH)
        mi = unreal.EditorAssetLibrary.load_asset(MI_PATH)
        skel = False
        if isinstance(master, unreal.Material):
            skel = bool(master.get_editor_property("used_with_skeletal_mesh"))
        self.checks.update({
            "master_loaded": bool(master),
            "master_used_with_skeletal_mesh": skel,
            "mi_loaded": bool(mi),
            "rhi": "d3d12(expected)",
        })
        log(f"material checks: master={bool(master)} skel={skel} mi={bool(mi)}")
        if not master or not skel:
            unreal.log_error(f"{TAG} FAIL-CLOSED: master missing or not UsedWithSkeletalMesh")
            self.finish(ok=False)
            return

        world = editor_world()
        eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

        try:
            light = eas.spawn_actor_from_class(
                unreal.DirectionalLight, V(EZ_SF[0], EZ_SF[1], 8000), rot(-55.0, 40.0), True)
            if light:
                self.spawned.append(light)
                try:
                    lc = light.get_component_by_class(unreal.DirectionalLightComponent)
                    if lc:
                        lc.set_intensity(12.0)
                        lc.set_editor_property("intensity", 12.0)
                except Exception as exc:
                    log(f"light intensity: {exc}")
            sky = eas.spawn_actor_from_class(unreal.SkyLight, V(0, 0, 1000), unreal.Rotator(0, 0, 0), True)
            if sky:
                self.spawned.append(sky)
        except Exception as exc:
            log(f"lights: {exc}")

        cls = unreal.EditorAssetLibrary.load_blueprint_class(CHARGER_BP)
        gz = ground_z(world, EZ_SF[0], EZ_SF[1], 0.0)
        self.checks["ground_z"] = gz
        if cls:
            fwd = bearing_vec(EZ_SF_BEARING, 1000.0)
            yaw = math.degrees(math.atan2(fwd[1], fwd[0]))
            self.car = eas.spawn_actor_from_class(
                cls, V(EZ_SF[0], EZ_SF[1], gz + 40.0), rot(0.0, yaw), True)
            if self.car:
                self.spawned.append(self.car)
                log(f"spawned {self.car.get_name()}")
                # C++ floor path (now BlueprintCallable) — preferred for log cue
                called = False
                for name in ("apply_charger_visual_material_floor", "ApplyChargerVisualMaterialFloor"):
                    fn = getattr(self.car, name, None)
                    if callable(fn):
                        try:
                            fn()
                            log(f"called {name}")
                            called = True
                            break
                        except Exception as exc:
                            log(f"{name} failed: {exc}")
                # Also ApplyVehicleLook Hellcat via enum
                try:
                    look_enum = unreal.EVehicleLook
                    self.car.apply_vehicle_look(look_enum.HELLCAT)
                    log("called apply_vehicle_look(HELLCAT)")
                    called = True
                except Exception as exc:
                    log(f"apply_vehicle_look failed: {exc}")
                if not called:
                    body = mi or master
                    mesh = None
                    try:
                        mesh = self.car.get_mesh()
                    except Exception:
                        try:
                            mesh = self.car.get_editor_property("mesh")
                        except Exception:
                            mesh = None
                    if mesh and body:
                        n = int(mesh.get_num_materials())
                        for i in range(max(1, n)):
                            mesh.set_material(i, body)
                        log(f"manual floor {body.get_name()} on {n} slots")
                # inspect slots
                names = []
                try:
                    mesh = self.car.get_mesh()
                    n = int(mesh.get_num_materials())
                    for i in range(n):
                        m = mesh.get_material(i)
                        names.append(m.get_name() if m else "None")
                except Exception as exc:
                    log(f"slot inspect: {exc}")
                self.checks["body_slots"] = names
                self.checks["floor_cpp_called"] = called
                log(f"body slots: {names}")
        self.checks["car_spawned"] = bool(self.car)

        self.cam = eas.spawn_actor_from_class(unreal.CameraActor, V(0, 0, 500), unreal.Rotator(0, 0, 0), True)
        self.spawned.append(self.cam)
        ox, oy = bearing_vec(EZ_SF_BEARING + 140.0, 450.0)
        cam_loc = V(EZ_SF[0] + ox, EZ_SF[1] + oy, gz + 140.0)
        look_at = V(EZ_SF[0], EZ_SF[1], gz + 70.0)
        look = unreal.MathLibrary.find_look_at_rotation(cam_loc, look_at)
        self.cam.set_actor_location_and_rotation(cam_loc, look, False, True)
        try:
            cc = self.cam.get_editor_property("camera_component")
            cc.set_editor_property("constrain_aspect_ratio", False)
            cc.set_editor_property("field_of_view", 55.0)
        except Exception:
            pass
        try:
            les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
            les.editor_set_game_view(True)
            les.pilot_level_actor(self.cam)
        except Exception as exc:
            log(f"pilot: {exc}")
        try:
            ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
            ues.set_level_viewport_camera_info(cam_loc, look)
        except Exception as exc:
            log(f"viewport cam: {exc}")

        for c in ("r.Streaming.FullyLoadUsedTextures 1", "r.ScreenPercentage 100",
                  "r.MotionBlurQuality 0", "r.EyeAdaptationQuality 0",
                  "r.DefaultFeature.AutoExposure 0"):
            cvar(c)
        log(f"warmup {WARMUP_S}s")
        self.goto("warmup")

    def do_shot(self):
        self.shot_dir = os.path.abspath(unreal.Paths.screen_shot_dir())
        self.dest = os.path.join(OUT_DIR, "S_car_body_paint_close.png").replace("\\", "/")
        self.before = set(pngs(self.shot_dir)) | set(pngs(OUT_DIR))
        # Prefer simple HighResShot without filename first if needed — try with filename like WE
        cvar(f"HighResShot {RES} filename={self.dest}")
        log(f"HighResShot {RES} -> {self.dest} (shot_dir={self.shot_dir})")
        self.goto("flush")

    def do_flush(self):
        if self.dest and os.path.exists(self.dest) and os.path.getsize(self.dest) > 1000:
            self.checks["still"] = self.dest
            self.checks["still_bytes"] = os.path.getsize(self.dest)
            log(f"still ready {self.dest} ({self.checks['still_bytes']} bytes)")
            self.finish(ok=True)
            return
        new = [p for p in pngs(self.shot_dir) + pngs(OUT_DIR) if p not in self.before]
        if new and self.elapsed() > 2.5:
            newest = max(new, key=os.path.getmtime)
            shutil.copy2(newest, self.dest)
            self.checks["still"] = self.dest
            self.checks["still_bytes"] = os.path.getsize(self.dest)
            self.checks["copied_from"] = newest
            log(f"still copied from {newest} -> {self.dest} ({self.checks['still_bytes']} bytes)")
            self.finish(ok=True)
            return
        if self.elapsed() > 35:
            # last resort: bare HighResShot then wait more
            if not self.checks.get("retried_bare_shot"):
                self.checks["retried_bare_shot"] = True
                self.before = set(pngs(self.shot_dir)) | set(pngs(OUT_DIR))
                cvar("HighResShot 1920x1080")
                log("retry bare HighResShot 1920x1080")
                self.t0 = time.time()
                return
            unreal.log_error(f"{TAG} no PNG after flush timeout")
            self.checks["still_error"] = "no PNG after flush timeout"
            self.finish(ok=False)

    def finish(self, ok=True):
        path = os.path.join(OUT_DIR, "verify_checks.json")
        self.checks["ok"] = ok
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.checks, f, indent=2)
        log(f"wrote {path} ok={ok}")
        try:
            les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
            les.eject_pilot_level_actor()
        except Exception:
            pass
        eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        for a in self.spawned:
            try:
                eas.destroy_actor(a)
            except Exception:
                pass
        self.phase = "done"
        if AUTO_QUIT:
            log("RGPS_STILLS_QUIT=1 -> quit_editor (no save)")
            unreal.SystemLibrary.quit_editor()


_runner = Runner()


def _on_tick(dt):
    if not _runner.tick(dt):
        try:
            unreal.unregister_slate_post_tick_callback(_runner.handle)
        except Exception:
            pass


_runner.handle = unreal.register_slate_post_tick_callback(_on_tick)
log(f"registered tick; out={OUT_DIR} quit={AUTO_QUIT} commit={git_sha()}")
