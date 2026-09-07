# Cleveland reference contract — D1

Lumen Helix Solutions · 2026-09-07 · **Reference discovery; geography not certified**

Use a historically grounded airport course, contemporary source-dated Cleveland
surroundings and raceGPS event dressing. The proposed historical reference is 2006;
do not relabel the later circuit as the original 1982 Cleveland 500 layout.

| Source | Confirmed use | Still required |
|---|---|---|
| [Cleveland race history](https://case.edu/ech/articles/g/grand-prix-cleveland) | Event identity and airport setting | Dated course geometry; reconcile era-specific dimensions |
| [INDYCAR 2006 replay](https://www.indycar.com/videos/2024/12/12-06-FullRaceReplay-Cleveland-2006) | Official visual reference source located | Inspect footage, timestamp relevant views and compare to dated circuit plan; no footage distribution rights assumed |
| [Ohio imagery/elevation downloads](https://gis1.oit.ohio.gov/geodatadownload/) | Official access point for county/tile OSIP imagery and elevation | Select actual Cuyahoga/Burke tiles, confirm dates/resolution/coverage, terms and hashes |
| [USGS LidarExplorer](https://www.usgs.gov/tools/lidarexplorer) | Official discovery/download route for lidar and derived elevation | Identify actual project coverage, vertical datum, quality level and tile costs/sizes |
| Existing Cleveland level/spec in repository | Source files available for reuse inspection | No matching citypack, no historical layout or skyline correspondence proven |

Do not download an entire county before selecting the bounded course/skyline area.
The existence of a catalog is not proof a particular building's facade or historical
surface can be reconstructed. Source scans may require cleanup and specifically
modeled facades. CARLA/adapters must supply a tested useful output, not replace
missing location evidence with generic scenery.

The eventual source manifest must record source URL/provider, acquisition date,
survey/imagery date, bounding area, horizontal/vertical CRS, units, transform,
resolution, checksum, rights/attribution and confidence. Keep historical circuit
control points and temporary race boundaries separate from current street topology.

## Scene acceptance packet

1. At least three georeferenced camera viewpoints with real-source comparisons:
   landmark order/bearing, relative skyline heights and moving-camera parallax.
2. One representative race segment with final pavement, barriers, car and UI at
   sunset, twilight and midnight using the same dry-surface physics and geometry.
3. Declare reference location/date and solar orientation; do not place sunset
   arbitrarily behind the skyline from every camera.
4. Measure visibility at braking distances and opponent silhouette/route cues,
   including glare and exposure transitions, with effects reduced as well as enabled.
5. Record frame-time distributions, CPU/GPU budgets and source/build versions.
6. Demonstrate steering/braking/overtaking/contact/recovery against two physical
   opponents; a collision-free replay does not count as an opponent.
7. Traverse the internal urban diagnostic fixture for tight geometry, camera
   occlusion, grade separation and streaming before extending to a city-scale claim.

No photorealism, exact historical geometry, awards, virality or playable build is
certified by this reference document. These are production acceptance goals.
