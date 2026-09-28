import type { LauncherSettings } from "@racegps/launcher-settings";
import type { PathValidation } from "./lib/pathValidation";

export {};

declare global {
  interface Window {
    racegps: {
      getSettings: () => Promise<LauncherSettings>;
      saveSettings: (s: LauncherSettings) => Promise<void>;
      resetSettings: () => Promise<LauncherSettings>;
      validatePaths: () => Promise<PathValidation>;
      launchRace: () => Promise<{ ok: boolean; detail: string }>;
      launchWorkshop: () => Promise<{ ok: boolean; detail: string }>;
      openLogs: () => Promise<void>;
      openPath: (target: string) => Promise<{ ok: boolean; detail: string }>;
      runWorkshopCli: (
        argv: string[],
      ) => Promise<{
        code: number;
        stdout: string;
        stderr: string;
        logPath: string;
      }>;
    };
  }
}
