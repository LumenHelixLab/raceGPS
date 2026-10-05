let meta = #{
    name: "week-1",
    description: "Week 1 only: Compiler steel-thread CityPack v2 and Race-Loop placeholder CruiseSprint, then fail-closed verification",
    when_to_use: "Start of a raceGPS session when STATUS.md still lists Compiler and Race-Loop as the only live agents",
    phases: [
        #{ title: "Assign", detail: "Compiler and Race-Loop in parallel" },
        #{ title: "Verify", detail: "Compiler-Test and loop-test evidence, fail closed" },
    ],
};

let report_schema = #{
    "type": "object",
    "required": ["summary", "paths", "violations"],
    "properties": #{
        "summary": #{ "type": "string" },
        "paths": #{ "type": "array", "items": #{ "type": "string" } },
        "violations": #{ "type": "array", "items": #{ "type": "string" } },
    },
};

let verdict_schema = #{
    "type": "object",
    "required": ["passed", "evidence", "reason"],
    "properties": #{
        "passed": #{ "type": "boolean" },
        "evidence": #{ "type": "string" },
        "reason": #{ "type": "string" },
    },
};

phase("Assign");

let compiler_prompt = "";
compiler_prompt += "You are the raceGPS Compiler Agent. Read AGENTS.md, STATUS.md, docs/contracts/CITYPACK_V2.md, ";
compiler_prompt += "docs/agents/sub/compiler.md, tools/universal-city-compiler/, and tools/akron-semantic-compiler/osm_to_xodr.py ";
compiler_prompt += "with read_file/grep before editing. ";
compiler_prompt += "ONE TASK: emit citypacks/steel-thread-001/ as a valid checksummed CityPack v2. ";
compiler_prompt += "Create tools/universal-city-compiler/fixtures/steel_thread.osm (2 highway ways sharing one node, 1 building way). ";
compiler_prompt += "Do not call Overpass. Do not compile Akron. Do not touch UE code. Do not import or call CARLA. ";
compiler_prompt += "Python 3.11 compiler only. Reuse generate_xodr from osm_to_xodr.py (or move an equivalent into universal-city-compiler). ";
compiler_prompt += "Pack must contain manifest.json, attribution.json, checksums.json, roads.xodr, roads.json, buildings.json, ";
compiler_prompt += "routes.json, spawn_points.json. statistics.roads=2, junctions=1, buildings=1. format=racegps-citypack-v2. ";
compiler_prompt += "JSON geometry is WGS84 lat/lon. Add tests/test_citypack_v2_steel_thread.py for schema, 2/1/1 counts, and hash-repeat. ";
compiler_prompt += "Run pytest on that test file. Return {summary, paths, violations}. violations is empty only if tests passed.";

let raceloop_prompt = "";
raceloop_prompt += "You are the raceGPS Race-Loop Agent. Read AGENTS.md, STATUS.md, docs/agents/sub/race-loop.md, ";
raceloop_prompt += "apps/unreal-akron-beta/Source/raceGPSAkronBeta/Public/CruiseSprintGameMode.h, ";
raceloop_prompt += "apps/unreal-akron-beta/Source/raceGPSAkronBeta/Private/CruiseSprintGameMode.cpp, and ";
raceloop_prompt += "apps/unreal-akron-beta/Source/raceGPSAkronBeta/Private/Tests/raceGPSGameplayTests.cpp with read_file before editing. ";
raceloop_prompt += "ONE TASK: prove CruiseSprintGameMode on a stock placeholder level, independent of Akron geometry. ";
raceloop_prompt += "If citypack load yields no routes/spawns, install a hardcoded placeholder course (spawn + spline + at least 2 checkpoints) ";
raceloop_prompt += "in world units, not lat/lon Akron data. Do not require AkronWorld.umap. Do not import CARLA vehicles. ";
raceloop_prompt += "Do not gate course validity on average speed, collision count, or a mandatory loop. Do not bump the engine off 5.5. ";
raceloop_prompt += "Expand raceGPSGameplayTests.cpp with tests for Loading -> Countdown -> Racing -> checkpoint advance -> Finish -> results payload. ";
raceloop_prompt += "Scoring math tests already exist; add the LOOP. Keep changes inside the raceGPSAkronBeta C++ module. ";
raceloop_prompt += "Return {summary, paths, violations}.";

let assign_jobs = [];
assign_jobs.push(#{
    prompt: compiler_prompt,
    label: "compiler",
    capability_mode: "all",
    output_schema: report_schema,
});
assign_jobs.push(#{
    prompt: raceloop_prompt,
    label: "race-loop",
    capability_mode: "all",
    output_schema: report_schema,
});
let assign_results = parallel(assign_jobs);

let compiler_r = assign_results[0];
let race_r = assign_results[1];
let assign_violations = [];
if (compiler_r == () || compiler_r.success != true) {
    assign_violations.push("Compiler agent failed or returned no result");
} else if (compiler_r.output.violations != ()) {
    for v in compiler_r.output.violations { assign_violations.push(v); }
}
if (race_r == () || race_r.success != true) {
    assign_violations.push("Race-Loop agent failed or returned no result");
} else if (race_r.output.violations != ()) {
    for v in race_r.output.violations { assign_violations.push(v); }
}

phase("Verify");

let v_compiler_prompt = "";
v_compiler_prompt += "You are the raceGPS Compiler-Test Agent (Verification). Fail closed. ";
v_compiler_prompt += "Read docs/contracts/CITYPACK_V2.md and inspect citypacks/steel-thread-001/ with list_dir and read_file. ";
v_compiler_prompt += "Run pytest tests/test_citypack_v2_steel_thread.py. ";
v_compiler_prompt += "Set passed=true only if the pack exists, format is racegps-citypack-v2, statistics are 2 roads / 1 junction / 1 building, ";
v_compiler_prompt += "checksums cover every file except checksums.json, roads.xodr root is OpenDRIVE, and pytest passed. ";
v_compiler_prompt += "If any of that is missing, passed=false. evidence must cite real paths or command output, not a self-report.";

let v_loop_prompt = "";
v_loop_prompt += "You are the raceGPS Verification skeptic for the placeholder gameplay loop. Fail closed. ";
v_loop_prompt += "Read CruiseSprintGameMode.h/.cpp and raceGPSGameplayTests.cpp. ";
v_loop_prompt += "Set passed=true only if you independently see (1) a placeholder course path that does not depend on Akron citypack geometry ";
v_loop_prompt += "and (2) automation tests covering Loading -> Countdown -> Racing -> checkpoint -> Finish. ";
v_loop_prompt += "C++ scoring tests alone are not enough. Missing UE editor does not count as a PIE pass. ";
v_loop_prompt += "passed=false if evidence is missing. Do not claim Section 2.2.";

let vjobs = [];
vjobs.push(#{
    prompt: v_compiler_prompt,
    label: "compiler-test",
    capability_mode: "execute",
    output_schema: verdict_schema,
});
vjobs.push(#{
    prompt: v_loop_prompt,
    label: "loop-test",
    capability_mode: "read-only",
    output_schema: verdict_schema,
});
let verdicts = parallel(vjobs);

let pack_passed = false;
let loop_passed = false;
let pack_evidence = "unverified";
let loop_evidence = "unverified";
if (verdicts[0] != () && verdicts[0].success && verdicts[0].output.passed == true
    && verdicts[0].output.evidence != () && verdicts[0].output.evidence != "") {
    pack_passed = true;
    pack_evidence = verdicts[0].output.evidence;
}
if (verdicts[1] != () && verdicts[1].success && verdicts[1].output.passed == true
    && verdicts[1].output.evidence != () && verdicts[1].output.evidence != "") {
    loop_passed = true;
    loop_evidence = verdicts[1].output.evidence;
}

log("steel-thread pack passed=" + pack_passed.to_string());
log("placeholder loop passed=" + loop_passed.to_string());

let summary = "Week 1 verification: pack=" + pack_passed.to_string() + " loop=" + loop_passed.to_string();
if (assign_violations.len() > 0) {
    summary += " assign_violations=" + assign_violations.len().to_string();
}

complete(#{
    summary: summary,
    pack_passed: pack_passed,
    loop_passed: loop_passed,
    pack_evidence: pack_evidence,
    loop_evidence: loop_evidence,
    assign_violations: assign_violations,
});
