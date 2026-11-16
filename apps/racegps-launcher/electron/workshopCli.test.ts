import assert from "node:assert/strict";
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import {
  buildAkronCompileCommand,
  buildRgpackExportArgv,
  buildRgpackValidateArgv,
  runPythonModule,
} from "./workshopCli.ts";

const worktreeRoot = fileURLToPath(new URL("../../../", import.meta.url));

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
  const cmd = buildAkronCompileCommand(worktreeRoot);
  assert.equal(
    path.relative(worktreeRoot, cmd.cwd).split(path.sep).join("/"),
    "tools/akron-semantic-compiler",
  );
  assert.deepEqual(cmd.argv, ["compile_akron.py"]);
  assert.ok(existsSync(path.join(cmd.cwd, cmd.argv[0])));
});

test("Workshop exports and validates a real offline pack, rejecting tampered geometry", async (t) => {
  const temp = mkdtempSync(path.join(os.tmpdir(), "racegps-workshop-"));
  t.after(() => rmSync(temp, { recursive: true, force: true }));
  const outDir = path.join(temp, "Burke track pack");
  const python = process.env.PYTHON || "python";

  const exported = await runPythonModule({
    python,
    worktreeRoot,
    argv: buildRgpackExportArgv(outDir, "workshop_smoke"),
  });
  assert.equal(exported.code, 0, exported.stderr || exported.stdout);
  const manifest = JSON.parse(readFileSync(path.join(outDir, "manifest.json"), "utf8"));
  assert.equal(manifest.packId, "workshop_smoke");
  assert.match(manifest.contentHash, /^sha256:[a-f0-9]{64}$/);

  const validated = await runPythonModule({
    python,
    worktreeRoot,
    argv: buildRgpackValidateArgv(outDir),
  });
  assert.equal(validated.code, 0, validated.stderr || validated.stdout);
  assert.match(validated.stdout, /RESULT\s+PASS/);

  writeFileSync(path.join(outDir, "streets.json"), "{}\n");
  const tampered = await runPythonModule({
    python,
    worktreeRoot,
    argv: buildRgpackValidateArgv(outDir),
  });
  assert.equal(tampered.code, 1);
  assert.match(tampered.stderr, /contentHash mismatch/);
});
