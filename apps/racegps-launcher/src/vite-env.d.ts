import type { LauncherSettings } from "@racegps/launcher-settings";

export {};

declare global {
  interface Window {
    racegps: {
      getSettings: () => Promise<LauncherSettings>;
      saveSettings: (s: LauncherSettings) => Promise<void>;
      resetSettings: () => Promise<LauncherSettings>;
      validatePaths: () => Promise<unknown>;
      launchRace: () => Promise<{ ok: boolean; detail: string }>;
      launchWorkshop: () => Promise<{ ok: boolean; detail: string }>;
      openLogs: () => Promise<void>;
      runWorkshopCli: (
        argv: string[],
      ) => Promise<{ code: number; stdout: string; stderr: string }>;
    };
  }
}
