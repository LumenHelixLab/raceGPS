import type { LauncherSettings } from "./schema.ts";

const ROOT = "C:\\projects\\raceGPS-grokbot-cleveland";
const AKRON = `${ROOT}\\apps\\unreal-akron-beta`;

export const DEFAULT_SETTINGS: LauncherSettings = {
  schemaVersion: 1,
  raceMode: "package",
  paths: {
    worktreeRoot: ROOT,
    devBat: `${AKRON}\\LaunchClevelandRace.bat`,
    packageExe: `${AKRON}\\PackagedBuilds\\Win64\\raceGPSRace.exe`,
    workshopPython: `${ROOT}\\.venv-grokbot\\Scripts\\python.exe`,
    uproject: `${AKRON}\\raceGPSAkronBeta.uproject`,
    logDir: `${AKRON}\\Saved\\Logs`,
  },
  gpuNote: "",
  firstRunCompleted: false,
  lastLaunch: { target: null, at: null, ok: null },
};
