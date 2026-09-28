import { contextBridge, ipcRenderer } from "electron";
import type { LauncherSettings } from "@racegps/launcher-settings";

contextBridge.exposeInMainWorld("racegps", {
  getSettings: (): Promise<LauncherSettings> => ipcRenderer.invoke("settings:get"),
  saveSettings: (s: LauncherSettings): Promise<void> =>
    ipcRenderer.invoke("settings:save", s),
  resetSettings: (): Promise<LauncherSettings> => ipcRenderer.invoke("settings:reset"),
  validatePaths: (): Promise<unknown> => ipcRenderer.invoke("paths:validate"),
  launchRace: (): Promise<{ ok: boolean; detail: string }> =>
    ipcRenderer.invoke("launch:race"),
  launchWorkshop: (): Promise<{ ok: boolean; detail: string }> =>
    ipcRenderer.invoke("launch:workshop"),
  openLogs: (): Promise<void> => ipcRenderer.invoke("logs:open"),
  openPath: (target: string): Promise<{ ok: boolean; detail: string }> =>
    ipcRenderer.invoke("shell:openPath", target),
  runWorkshopCli: (
    argv: string[],
  ): Promise<{ code: number; stdout: string; stderr: string; logPath: string }> =>
    ipcRenderer.invoke("workshop:cli", argv),
});
