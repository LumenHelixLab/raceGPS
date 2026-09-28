import type { LauncherSettings } from "@racegps/launcher-settings";

export type StatusChip = {
  id: string;
  label: string;
  tone: "ok" | "warn" | "fail";
};

export type PathValidation = {
  devBatOk: boolean;
  packageExeOk: boolean;
  workshopPythonOk: boolean;
  uprojectOk: boolean;
  awaitingBuild: boolean;
  chips: StatusChip[];
};

/**
 * Pure path checks for launcher settings.
 * Inject `exists` (e.g. fs.existsSync in Electron main). Renderer uses IPC
 * `paths:validate` so the browser bundle never imports node:fs.
 */
export function validateLauncherPaths(
  settings: LauncherSettings,
  exists: (p: string) => boolean = () => false,
): PathValidation {
  const devBatOk = exists(settings.paths.devBat);
  const packageExeOk = exists(settings.paths.packageExe);
  const workshopPythonOk = exists(settings.paths.workshopPython);
  const uprojectOk = exists(settings.paths.uproject);
  const awaitingBuild = settings.raceMode === "package" && !packageExeOk;
  const chips: StatusChip[] = [
    {
      id: "mode",
      label: `Mode: ${settings.raceMode}`,
      tone: "ok",
    },
    {
      id: "devBat",
      label: devBatOk ? "Dev bat found" : "Dev bat missing",
      tone: devBatOk ? "ok" : "fail",
    },
    {
      id: "package",
      label: packageExeOk ? "Package exe found" : "Package awaiting build",
      tone: packageExeOk ? "ok" : "warn",
    },
    {
      id: "python",
      label: workshopPythonOk ? "Workshop python OK" : "Workshop python missing",
      tone: workshopPythonOk ? "ok" : "fail",
    },
  ];
  return {
    devBatOk,
    packageExeOk,
    workshopPythonOk,
    uprojectOk,
    awaitingBuild,
    chips,
  };
}
