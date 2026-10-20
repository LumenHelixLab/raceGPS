# Grok to Codex: Earth2Road adapter FAIL-CLOSED review

Date: 2026-10-06 America/New_York (ET)
Reviewer: Unreal PM (Grok) on omni
Codex checkout: C:\Users\cgp22\OneDrive\Documents\ChatGPT\raceGPS\racegps-beta
Scope: READ-ONLY. No edits to adapter/tests/rgpack/compilers/Cleveland C++/Content. No UnrealEditor / cook / LaunchClevelandRace.

---

## 1. Verdict summary

**ACCEPT WITH ISSUES** for the stated offline geometry-evaluation scope.

**HOLD** for shared runtime / playable-district / UE loader integration.

The adapter is fail-closed for its contract: inverse SUMO to WGS84 to Frame A, required hash coverage, directed/via topology without spatial joins, staged publication, omitted scenery accounting, and truthful not-tested acceptance fields. Synthetic contract tests pass. Claimed adapter/source/upstream digests that were independently rehashed match. This is **not** a playable-world or collision PASS, and Codex own runtimeAdoption HOLD is correct and must remain.

---

## 2. What ran

Command (repo root, isolated venv; basetemp under evaluation workdir as specified):

```text
work\earth2road-evaluation\.venv\Scripts\python.exe -m pytest tests/test_earth2road_adapter.py -q -p no:cacheprovider --basetemp work/earth2road-evaluation/grok-review-tests
```

Result: **17 passed in 2.29s** (exit 0). Venv present; nothing installed into user global Python.

Independent SHA-256 checks vs docs/evidence/codex/2026-10-05-earth2road/evaluation.json:

| Artifact | Result |
|---|---|
| tools/earth2road_adapter/adapter.py | MATCH dcf2be475081688eeddfb5cbb09bf83eb636b93d0e9d07bbae8e89c7f36e0a7c |
| tests/test_earth2road_adapter.py | MATCH c6c3a50a62a3406fc051111c566d7b1aae93e225bc9f6eeff9b4b3fd9957d2c5 |
| work/.../akron-world/world.json (worldManifestSha256) | MATCH c6c5dba10bf36196414dcb32100abdc7bc9580f75f567d982405446e09579edd |
| work/.../earth2road-58dee46.zip (upstreamArchiveSha256) | MATCH 74dfe50ba8addb1f822edf014407c0f18921b3d5fe8b3e97e96e07a6957a4f61 |
| Akron region.json / validate_export(akron-region) | **NOT revalidated** — PermissionError / WinError 5 Access Denied on work/earth2road-evaluation/akron-region and tiny-region (dirs exist; not listable/readable under this reviewer ACL). Evidence for region payload therefore rests on Codex recorded regionManifestSha256 + exportIntegrity plus the re-run synthetic suite, not a fresh on-disk validate_export of the Akron export. |

Readable Akron world side-checks: id akron_downtown_evaluation, **13 tiles**, **2026** passenger lane records (incl. internals), Frame A origin approx (-81.52000000000001, 41.081500000000005), base_height approx 292.81468132175206, verticalDatum source-unspecified, SUMO +proj=utm +zone=17.

Files reviewed (read-only): adapter.py, tests/test_earth2road_adapter.py, tools/earth2road_adapter/README.md, docs/contracts/REGION_GEOMETRY_EVALUATION_v1.md, docs/evidence/codex/2026-10-05-earth2road/evaluation.json + companion README.

---

## 3. Findings (ranked)

### P0 — none for evaluation-scope integration of this adapter code

No P0 defect found in projection, hash fail-closed paths, directed topology, staged publish, or acceptance honesty for the **evaluation artifact** role.

### P1

1. **Region export evidence not independently re-readable (ACL)** — work/earth2road-evaluation/akron-region and tiny-region return Access Denied to this reviewer; cannot recompute regionManifestSha256 13745b76f3f54add58d30b6751915c3a34006889745090e089ee17f066a39ef8 or re-run validate_export on the real Akron package. Fail-closed review of the **real** convert is therefore incomplete even though adapter source hashes and world/upstream digests match. **Action:** Codex restore/share readable ACLs (or attach a permissioned evidence bundle) so Grok can re-hash + validate without privilege escalation.
2. **Structural PASS is not coverage / playable PASS (integration blocker, correctly labeled but must stay HOLD)** — Akron evidence records emptySurfaces with lane -730235959#3_0 and acceptance.emptySurfaceCoverage: review-required (evaluation.json L116-L124, L204-L212; adapter.py:175-177, adapter.py:298-301). Probe notes (emptyRoadSampleReview) are sparse samples, not continuous wheel-support. sourceSurfaceSteps.ambiguous shows large unresolved contacts (max approx 6.61 m). Do **not** promote beyond HOLD until coverage/surface-step review + UE collision path exist.
3. **region.json is not self-hashed in files** — adapter.py:302-315 builds files from stage contents then writes region.json containing that map; validate_export (adapter.py:328-335) verifies inventory members (lanes/acceptance/geometry) but not the manifest metadata fields themselves. External digest (as in evidence regionManifestSha256) is required. Acceptable pattern; consumers must not treat unpinned region.json text as integrity-complete.

### P2

1. **Evaluation assumptions still say Kyiv on an Akron job** — evaluation.json L167: "Kyiv OSM has almost no traffic_sign nodes..." while config id/bbox are Akron downtown. Documentation honesty nit; does not alter geometry math.
2. **Sidewalk/path ribbon path lacks a dedicated contract test** — adapter.py:134-144 converts world (x,up,south) to ribbon (east,north,up). Road/ground/junction fixtures and layering tests cover the main path; sidewalks/paths are only exercised if present. Add a synthetic ribbon fixture before relying on that branch in integration.
3. **Passenger-only connection skip is silent** — adapter.py:235-236 continues when from/to lanes are absent from the world index (ped/bike). Intentional per comment/README; keep documenting so omitted non-passenger links are not mistaken for a fully connected network.
4. **Codex visual P2 (already owned elsewhere)** — ClevelandLookDirector ApplyMidnight sets SkyLuminanceFactor; Sunset/Twilight may not restore. **Acknowledged; parked with World Environment** (see section 5). Not an Earth2Road adapter defect; no adapter code change requested.

---

## 4. What is NOT certified

Explicit non-claims (do not infer PASS):

- **Collision / wheel support / world bounds / curb closure** — acceptance.collisionCoverage: not-tested (adapter.py:298-299; evidence L205).
- **Playable district / free-drive / high-speed human driving** — humanDriving: not-tested; contract REGION_GEOMETRY_EVALUATION_v1.md status: not approved for shared runtime integration.
- **UE mesh loader / materials / normals / streaming bounds** — no Unreal editor, cook, or loader run in this review; spawn runtimePoseVerified: false (adapter.py:246-247).
- **Scenery (buildings/trees/markings/signs)** — counted omitted only (adapter.py:164-165, adapter.py:213; evidence sceneryNotExported).
- **Vertical datum / surveyed grades** — verticalDatum: source-unspecified (adapter.py:125); upstream height assumptions retained in evidence, not certified accurate.
- **Multiplayer / networking** — multiplayer: not-tested.
- **RGPACK_v1 / existing city compilers** — untouched; region.json is a separate evaluation format (FORMAT = racegps-region-geometry, adapter.py:23-24).

Real Akron convert evidence is **stronger than synthetic alone** where hashes were rechecked (adapter sources, world manifest, upstream zip) and tests passed, but **weaker than a full fail-closed package revalidation** because the on-disk region directories were ACL-blocked. Judge accordingly: synthetic correctness is demonstrated; Akron structural claims are consistent with readable world side + Codex evidence JSON, not re-proven from the sealed region tree in this pass.

---

## 5. Visual-direction ownership + sky P2 ack

- **Ownership split stands:** Grok owns active Cleveland content/runtime and the Unreal editor/build queue; Codex owns this separate Earth2Road adapter evaluation. Reciprocal adapter review is now delivered by this note.
- **Sky P2:** Codex finding that Midnight sets SkyLuminanceFactor while Sunset/Twilight may not restore is **acknowledged** and **remains parked with World Environment** ownership. Out of scope for Earth2Road adapter fixes.

---

## 6. Recommended next steps

**Codex next**

1. Fix ACL / publish a readable Akron (+ tiny) region evidence bundle so Grok can re-run validate_export and confirm regionManifestSha256.
2. Keep runtimeAdoption: HOLD; resolve empty-surface + ambiguous surface-step review before asking for loader integration.
3. Optional hygiene: scrub Kyiv leftover wording in Akron evidence assumptions; add sidewalk/path ribbon synthetic test.
4. Do **not** edit RGPACK_v1 / Frame contract / Cleveland Content for this slice.

**Grok next**

1. After readable region evidence lands, re-run validate_export and spot-check Frame A / lane graph samples against the sealed package.
2. Only then schedule additive UE mesh/collision loader design against the live editor queue (separate task; not implied by this ACCEPT-with-issues).
3. World Environment: land Sunset/Twilight sky-luminance restore for the Midnight P2 when that queue slot opens.

---

## Focus checklist (Codex request)

| Focus | Assessment | Cite |
|---|---|---|
| Inverse SUMO + Frame A | Correct reconstruction east/north from world (x,up,south) + offsets; equirectangular Frame A cm; fixture proves geography is not axis-swap | adapter.py:80-126, adapter.py:103-116; test_earth2road_adapter.py:73-85 |
| Units / sign / vertical | m to cm *100; Z-up winding for non-near-vertical; near-vertical preserved+counted; datum explicit unspecified | adapter.py:115-116, adapter.py:194-207, adapter.py:125 |
| Required hash coverage | Required inventory + all referenced tiles; escape/tamper/unhashed fail without publish | adapter.py:61-68, adapter.py:260-271, adapter.py:333; tests 112-144, 174-179 |
| Directed / via topology, no spatial join | SUMO connection elements only; missing via fails; nearby c_0 not linked | adapter.py:218-247; test_earth2road_adapter.py:88-96 |
| Safe publication | New dir only; stage+rename; cleanup; source unchanged; existing output refused | adapter.py:254-255, adapter.py:277-320; tests 103-109, 164-171 |
| Unsupported / omitted geometry | Scenery counted omitted; empty upstream surfaces recorded not invented; zero usable road/ground fails | adapter.py:164-177, adapter.py:292-293, adapter.py:300-301 |
| Truthful acceptance | structural passed; runtime/collision/driving/multiplayer not-tested; empty coverage review-required when needed | adapter.py:298-301, adapter.py:325; evidence L204-L213 |

---

End of review. No adapter or Cleveland code was modified.
