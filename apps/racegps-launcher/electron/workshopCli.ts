import { spawn } from "node:child_process";
import path from "node:path";

export type WorkshopCliResult = {
  code: number;
  stdout: string;
  stderr: string;
};

export function buildRgpackExportArgv(outDir: string, packId: string): string[] {
  return [
    "-m",
    "rgpack",
    "export-overpass",
    "--fixture",
    "-o",
    outDir,
    "--pack-id",
    packId,
  ];
}

export function buildRgpackValidateArgv(packDir: string): string[] {
  return ["-m", "rgpack", "validate", packDir];
}

/** Secondary reference path — Akron semantic compiler (not Unreal). */
export function buildAkronCompileCommand(worktreeRoot: string): {
  cwd: string;
  argv: string[];
} {
  return {
    cwd: path.join(worktreeRoot, "tools", "akron-semantic-compiler"),
    argv: ["compile_akron.py"],
  };
}

export function runPythonModule(opts: {
  python: string;
  worktreeRoot: string;
  argv: string[];
  cwd?: string;
}): Promise<WorkshopCliResult> {
  const tools = path.join(opts.worktreeRoot, "tools");
  const cwd = opts.cwd ?? opts.worktreeRoot;
  return new Promise((resolve) => {
    const child = spawn(opts.python, opts.argv, {
      cwd,
      env: { ...process.env, PYTHONPATH: tools },
      windowsHide: true,
    });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (d: Buffer | string) => {
      stdout += String(d);
    });
    child.stderr.on("data", (d: Buffer | string) => {
      stderr += String(d);
    });
    child.on("error", (err) => {
      resolve({
        code: 1,
        stdout,
        stderr: `${stderr}${stderr ? "\n" : ""}${err.message}`,
      });
    });
    child.on("close", (code) => {
      resolve({ code: code ?? 1, stdout, stderr });
    });
  });
}
