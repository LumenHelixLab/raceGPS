# Preserve real Cleveland inputs and prevent false route/startup success

The current city pipeline can connect roads by proximity, label an open path as a
circuit, and begin a race after a fixed delay even when its road data is missing.
The committed Akron graph and OpenDRIVE also describe different road sets.

This branch introduces explicit directed source-segment routing and an integrity
audit before packaging, preserves a real source-dated Cleveland airport extract,
and adds a deterministic offline context compiler. Runtime startup now waits for
road generation and exposes an actionable failure instead of silently selecting
Akron or starting early. The branch includes the preceding D1 build/CI fixes.

Validation: 224 Python tests passed, 5 skipped for the absent historical Akron OSM.
Two independent Cleveland compiles matched all ten files byte for byte. Real Akron
integrity checks correctly fail. The Cleveland research bundle correctly remains
not race ready. Unreal preflight failed because no UE 5.7 host is available here.

Keep this PR in draft. C++/Slate has not been compiled. Coordinate axes/units must be
migrated consistently across the importer, level specs, scenery and scene assets;
the historical circuit and physical/visual gameplay gates remain open. This is not
a playable-demo release. See docs/plans/NEXT_FIVE_GATES_EXECUTION.md for evidence,
known blockers and exact host commands.
