"""_ca_ribbon_stills.py -- Course Architect one-pass Burke EZ ribbon stills (LOCAL HELPER, not in repo).

Reuses World Environment's proven recipe (_we_modeb_stills_capture.py, run 2, 2026-10-05):
UnrealEditor GUI, D3D12, /Game/Maps/Cleveland5_0KmWorld, transient ClevelandEnvironmentActor.LoadAndBuild
+ ClevelandLookDirector.ApplyVisualMode, CameraActor piloted, HighResShot filename=..., quit_editor (no save).
No material/UV/exposure edits. Nothing saved. GlobalDefaultGameMode untouched.
Shots: overhead + driver in Sunset (launcher default preset), then the same pair in Midnight (WE's preset).
"""
import json, math, os, time
import unreal

TAG = "[CA stills]"
MAP = "/Game/Maps/Cleveland5_0KmWorld"
OUT_DIR = r"C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\burke-ez-ribbon\stills\ca-pass"
LINE = r"C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\citypacks\cleveland\burke_gp_1997\racing_line.json"
RES = "1920x1080"
WARMUP_S = 45.0
SETTLE_S = 5.0
DATE = "2026-10-05"


def log(m):
    unreal.log_warning(f"{TAG} {m}")


def V(x, y, z):
    return unreal.Vector(float(x), float(y), float(z))


def R(pitch, yaw):
    return unreal.Rotator(roll=0.0, pitch=float(pitch), yaw=float(yaw))


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def cvar(c):
    unreal.SystemLibrary.execute_console_command(world(), c)


def ground_z(x, y, default=0.0):
    try:
        hit = unreal.SystemLibrary.line_trace_single(world(), V(x, y, 50000), V(x, y, -50000),
            unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        hr = hit[1] if isinstance(hit, tuple) else hit
        t = hr.to_tuple()
        if t[0]:
            return float(t[5].z)
    except Exception as exc:  # noqa: BLE001
        log(f"ground trace failed {exc}")
    return default


# racing line -> Frame A cm (same formula family as UAkronXodrImporter::GeoToWorld)
d = json.load(open(LINE, encoding="utf-8"))
lat0, lon0 = d["origin"]["lat"], d["origin"]["lon"]
phi = math.radians(lat0)
MLAT = 111132.92 - 559.82 * math.cos(2 * phi) + 1.175 * math.cos(4 * phi)
MLON = 111412.84 * math.cos(phi) - 93.5 * math.cos(3 * phi)
P = [((s["lon"] - lon0) * MLON * 100.0, (s["lat"] - lat0) * MLAT * 100.0) for s in d["samples"]]
xs = [p[0] for p in P]; ys = [p[1] for p in P]
CX, CY = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2


class Cap:
    def __init__(self):
        self.phase = "load"; self.t = time.time(); self.spawned = []; self.idx = 0
        self.shots = []; self.results = []; self.h = None; self.env = None; self.look = None
        os.makedirs(OUT_DIR, exist_ok=True)

    def goto(self, p):
        self.phase = p; self.t = time.time()

    def el(self):
        return time.time() - self.t

    def tick(self, _dt):
        try:
            getattr(self, "p_" + self.phase)()
        except Exception as exc:  # noqa: BLE001
            unreal.log_error(f"{TAG} phase {self.phase} crashed: {exc}")
            self.goto("cleanup")

    def p_load(self):
        cur = world().get_path_name()
        if "Cleveland5_0KmWorld" not in cur:
            log(f"load_level {MAP} (current {cur})")
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
        self.goto("build")

    def p_build(self):
        if self.el() < 3.0:
            return
        eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        self.pre = set(a.get_path_name() for a in eas.get_all_level_actors())
        self.env = eas.spawn_actor_from_class(unreal.ClevelandEnvironmentActor, V(0, 0, 0), R(0, 0), True)
        self.spawned.append(self.env)
        self.env.set_editor_property("use_photo_skyline_backdrop", True)
        log(f"EnvActor LoadAndBuild -> {self.env.load_and_build()}")
        self.look = eas.spawn_actor_from_class(unreal.ClevelandLookDirector, V(0, 0, 0), R(0, 0), True)
        self.spawned.append(self.look)
        self.cam = eas.spawn_actor_from_class(unreal.CameraActor, V(0, 0, 500), R(0, 0), True)
        self.spawned.append(self.cam)
        self.cam.get_editor_property("camera_component").set_editor_property("constrain_aspect_ratio", False)
        # geometry
        i0, i1 = 3, 4
        dx, dy = P[i1][0] - P[i0][0], P[i1][1] - P[i0][1]
        yaw = math.degrees(math.atan2(dy, dx))
        gz = ground_z(P[i0][0], P[i0][1], 0.0)
        log(f"track bbox x[{min(xs):.0f},{max(xs):.0f}] y[{min(ys):.0f},{max(ys):.0f}] centre=({CX:.0f},{CY:.0f}) "
            f"S/F=({P[0][0]:.0f},{P[0][1]:.0f}) driver sample {i0} ground_z={gz:.1f} yaw={yaw:.1f}")
        over = dict(loc=V(CX, CY, 150000.0), rot=R(-90.0, 90.0), fov=60.0)
        drv = dict(loc=V(P[i0][0], P[i0][1], gz + 115.0), rot=R(-1.5, yaw), fov=80.0)
        for preset, suffix in (("SUNSET", ""), ("MIDNIGHT", "-midnight")):
            self.shots.append(dict(id=f"overhead{suffix}", preset=preset, **over))
            self.shots.append(dict(id=f"driver{suffix}", preset=preset, **drv))
        self.apply_preset("SUNSET")
        try:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_set_game_view(True)
        except Exception as exc:  # noqa: BLE001
            log(f"game view toggle failed {exc}")
        for c in ("r.Streaming.FullyLoadUsedTextures 1", "r.ScreenPercentage 100", "r.MotionBlurQuality 0"):
            cvar(c)
        log(f"built; warmup {WARMUP_S}s")
        self.cur_preset = "SUNSET"
        self.goto("warmup")

    def apply_preset(self, preset):
        mode = getattr(unreal.ClevelandVisualMode, preset)
        self.look.apply_visual_mode(mode)
        self.env.apply_look_mode(preset == "MIDNIGHT")
        log(f"LookDirector.ApplyVisualMode({preset}) + env.ApplyLookMode(midnight={preset == 'MIDNIGHT'})")

    def p_warmup(self):
        if self.el() >= WARMUP_S:
            self.goto("place")

    def p_place(self):
        if self.idx >= len(self.shots):
            self.goto("cleanup"); return
        s = self.shots[self.idx]
        extra = 0.0
        if s["preset"] != self.cur_preset:
            self.apply_preset(s["preset"]); self.cur_preset = s["preset"]; extra = 10.0
        self.cam.set_actor_location_and_rotation(s["loc"], s["rot"], False, True)
        self.cam.get_editor_property("camera_component").set_editor_property("field_of_view", s["fov"])
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).pilot_level_actor(self.cam)
        unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(s["loc"], s["rot"])
        log(f"{s['id']} preset={s['preset']} cam=({s['loc'].x:.0f},{s['loc'].y:.0f},{s['loc'].z:.0f}) "
            f"pitch={s['rot'].pitch:.1f} yaw={s['rot'].yaw:.1f} fov={s['fov']}")
        self.settle = SETTLE_S + extra
        self.goto("settle")

    def p_settle(self):
        if self.el() < self.settle:
            return
        s = self.shots[self.idx]
        s["dest"] = os.path.join(OUT_DIR, f"CA-{DATE}-{s['id']}.png")
        s["before"] = set(self.pngs(OUT_DIR)) | set(self.pngs(unreal.Paths.screen_shot_dir()))
        cvar(f"HighResShot {RES} filename={s['dest'].replace(os.sep, '/')}")
        log(f"{s['id']} HighResShot {RES} -> {s['dest']}")
        self.goto("flush")

    def p_flush(self):
        s = self.shots[self.idx]
        if os.path.exists(s["dest"]) and self.el() > 1.0:
            self.rec(s, s["dest"]); return
        new = [p for p in self.pngs(OUT_DIR) + self.pngs(unreal.Paths.screen_shot_dir()) if p not in s["before"]]
        if new and self.el() > 3.0:
            import shutil
            src = max(new, key=os.path.getmtime)
            if os.path.abspath(src) != os.path.abspath(s["dest"]):
                shutil.copy2(src, s["dest"])
            self.rec(s, s["dest"], src); return
        if self.el() > 30:
            unreal.log_error(f"{TAG} {s['id']} no PNG after 30 s")
            self.results.append({"id": s["id"], "error": "no PNG"}); self.idx += 1; self.goto("place")

    def rec(self, s, path, src=None):
        e = {"id": s["id"], "preset": s["preset"], "file": path, "bytes": os.path.getsize(path),
             "cam_loc_cm": [round(s["loc"].x), round(s["loc"].y), round(s["loc"].z)],
             "cam_pitch": s["rot"].pitch, "cam_yaw": round(s["rot"].yaw, 2), "fov": s["fov"]}
        if src:
            e["copied_from"] = src
        self.results.append(e)
        log(f"{s['id']} saved {path} ({e['bytes']} bytes)")
        self.idx += 1; self.goto("place")

    @staticmethod
    def pngs(dd):
        out = []
        for root, _d, fs in os.walk(dd):
            out += [os.path.join(root, f) for f in fs if f.lower().endswith(".png")]
        return out

    def p_cleanup(self):
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
        for a in eas.get_all_level_actors():
            try:
                if a.get_class().get_name() in {"DayNightCycle", "PostProcessController", "BuildingMeshGenerator"} \
                        and a.get_path_name() not in getattr(self, "pre", set()):
                    eas.destroy_actor(a)
            except Exception:  # noqa: BLE001
                pass
        with open(os.path.join(OUT_DIR, f"CA-{DATE}-capture-manifest.json"), "w", encoding="utf-8") as fh:
            json.dump({"tool": "_ca_ribbon_stills.py (local helper, C:/Users/cgp22/ca-stills-staging)",
                       "map": MAP, "mode": "UnrealEditor GUI editor world, D3D12 (no -game, no PIE, no NullRHI)",
                       "res": RES, "frame": "Frame A X=east Y=north Z-up cm (left-handed => mirrored vs compass)",
                       "line_bbox_cm": [min(xs), max(xs), min(ys), max(ys)],
                       "shots": self.results, "finished_local": time.strftime("%Y-%m-%d %H:%M:%S %z")}, fh, indent=2)
        log(f"DONE shots={len([r for r in self.results if 'file' in r])}/{len(self.shots)}; quitting editor (no save)")
        unreal.unregister_slate_post_tick_callback(self.h)
        unreal.SystemLibrary.quit_editor()


_C = Cap()
_C.h = unreal.register_slate_post_tick_callback(_C.tick)
log(f"armed out={OUT_DIR}")
