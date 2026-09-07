# Cleveland / Burke Lakefront — pinned context source

`snapshot.osm` is the unmodified OpenStreetMap API response for the bounded development
area recorded in `source.json`. Preserve its SHA-256 and source date when deriving
new data. © OpenStreetMap contributors; source/license and attribution details:
https://www.openstreetmap.org/copyright . Keep this attribution with redistributions
and review the applicable database terms for derived releases.

This is **contemporary context**, not a certified 2006 course, measured terrain,
photogrammetry, or premium art. A map response includes complete intersecting ways
that can extend beyond the requested bounding box. The compiler does not claim full
multipolygon/relation coverage. Airport runway/taxiway/apron features stay distinct
from highway routes; no route or championship ownership is assigned from this file.

From the repository root, produce a fresh research bundle without network calls:

```sh
python scripts/compile_snapshot.py --source data/sources/cleveland-burke/snapshot.osm --source-record data/sources/cleveland-burke/source.json --output build-evidence/cleveland-context-new --city-id cleveland-burke-context --origin 41.5178611 -81.6826389
python scripts/citypack_audit.py build-evidence/cleveland-context-new --report build-evidence/cleveland-context-readiness.json
```

The second command must currently fail: the bundle explicitly has no certified race
route or starting grid and is marked `release_ready: false`. Do not put it into the
shipping citypacks folder or relabel it as `cleveland_5.0km` to defeat that gate.
The origin is a provisional local reference, not a surveyed race control point.

For the historical layer, the provisional reference remains the official
[2006 race replay](https://www.indycar.com/videos/2024/12/12-06-FullRaceReplay-Cleveland-2006).
A dated plan, georeferenced controls and checked circuit boundaries are still needed.
