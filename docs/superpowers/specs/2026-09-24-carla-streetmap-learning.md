# CARLA / StreetMap learning notes — raceGPS streets (2026-09-24)

**Purpose:** Stop inventing road tech. Use known CARLA + OSM patterns.

## What CARLA actually teaches (UE5)

1. **Roads:** OSM → OpenDRIVE (`.xodr`) via `carla.Osm2Odr` / `config.py --osm-path`, then OpenDRIVE standalone mesh generation. Docs: https://carla-ue5.readthedocs.io/en/latest/tuto_G_openstreetmap/
2. **Full pretty maps:** OpenDRIVE *plus* FBX meshes (RoadRunner / custom) — XODR alone is driveable topology with basic meshes, not Midnight Club dress.
3. **Vehicles:** Chassis skeletal mesh + **separate door static meshes** on BP (Door_* bones). Lights/doors are API-driven parts, not morph targets.
4. **StreetMap plugin** (ue4plugins/StreetMap / carla forks): OSM → spline/street actors in editor. Often UE4-era — check UE5.7 fork before depending on it.

## raceGPS recommendation (playable downtown)

**Do not** stand up full CARLA server as the game runtime.

**Do** steal the data path:

| Stage | Tool | Output |
|-------|------|--------|
| 1 | Overpass / OSM extract (CLI Workshop) | road centerlines + highway class |
| 2 | Pack (`rgpack`) | WGS84 polylines + Frame A origin |
| 3 | Race | Driveable ribbon/mesh along centerlines (Chaos vehicle) |
| 4 later | Optional Osm2Odr or StreetMap | Better lane widths / junctions when needed |

First demo bbox: small Cleveland downtown (~1–2 km), provisional pack, Sunset, **dressed ground + sky — never black void**.

## Visual floor gate (non-negotiable)

Before calling anything a beta:

- [ ] Charger has doors (imported CARLA door meshes on BP)
- [ ] Headlights/bloom do not blow out the frame
- [ ] Car sits on real street mesh or clear asphalt ribbon, not infinite black
- [ ] Screenshot would not embarrass a Midnight Club reference side-by-side at thumbnail size

## Links

- CARLA OSM tutorial: https://carla-ue5.readthedocs.io/en/latest/tuto_G_openstreetmap/
- CARLA vehicle authoring (doors): https://carla-ue5.readthedocs.io/en/latest/tuto_content_authoring_vehicles/
- carla-content: https://bitbucket.org/carla-simulator/carla-content/src
- Attribution in-tree: `Content/Vehicles/CARLA-ATTRIBUTION.txt` (tag 0.10.0)
