import assert from "node:assert/strict";
import test from "node:test";
import {
  buildAkronCompileCommand,
  buildRgpackExportArgv,
  buildRgpackValidateArgv,
} from "./workshopCli.ts";

test("export uses fixture flag and out dir", () => {
  const argv = buildRgpackExportArgv(
    "C:\\packs\\burke",
    "burke_overpass_proof_v1",
  );
  assert.deepEqual(argv, [
    "-m",
    "rgpack",
    "export-overpass",
    "--fixture",
    "-o",
    "C:\\packs\\burke",
    "--pack-id",
    "burke_overpass_proof_v1",
  ]);
});

test("validate passes pack dir", () => {
  assert.deepEqual(buildRgpackValidateArgv("C:\\packs\\burke"), [
    "-m",
    "rgpack",
    "validate",
    "C:\\packs\\burke",
  ]);
});

test("akron compile command uses semantic compiler cwd", () => {
  const cmd = buildAkronCompileCommand("C:\\projects\\raceGPS-grokbot-cleveland");
  assert.equal(
    cmd.cwd,
    "C:\\projects\\raceGPS-grokbot-cleveland\\tools\\akron-semantic-compiler",
  );
  assert.deepEqual(cmd.argv, ["compile_akron.py"]);
});
