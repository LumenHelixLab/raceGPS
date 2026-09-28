import { app, BrowserWindow, ipcMain, shell } from "electron";
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import {
  loadSettings,
  resetSettings,
  saveSettings,
  settingsFilePath,
  type LauncherSettings,
} from "@racegps/launcher-settings";
import { validateLauncherPaths } from "../src/lib/pathValidation";

function settingsPath(): string {
  return settingsFilePath(app.getPath("appData"));
}

function createWindow(): void {
  const win = new BrowserWindow({
    width: 1100,
    height: 720,
    webPreferences: {
      preload: path.join(__dirname, "../preload/index.mjs"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  if (process.env.ELECTRON_RENDERER_URL) {
    win.loadURL(process.env.ELECTRON_RENDERER_URL);
  } else {
    win.loadFile(path.join(__dirname, "../renderer/index.html"));
  }
}

app.whenReady().then(() => {
  ipcMain.handle("settings:get", () => loadSettings(settingsPath()));
  ipcMain.handle("settings:save", (_e, s: LauncherSettings) => {
    saveSettings(settingsPath(), s);
  });
  ipcMain.handle("settings:reset", () => resetSettings(settingsPath()));

  ipcMain.handle("paths:validate", () => {
    const s = loadSettings(settingsPath());
    return validateLauncherPaths(s, fs.existsSync);
  });

  ipcMain.handle("launch:race", async () => {
    const s = loadSettings(settingsPath());
    const v = validateLauncherPaths(s, fs.existsSync);
    if (s.raceMode === "package") {
      if (!v.packageExeOk) {
        return {
          ok: false,
          detail:
            "Package mode awaiting build - switch to Dev, or point packageExe at a Chris-unlocked cook output (see docs/contracts/LAUNCHER_PATH_CONTRACT.md).",
        };
      }
      spawn(s.paths.packageExe, [], { detached: true, stdio: "ignore" }).unref();
      return { ok: true, detail: `spawned ${s.paths.packageExe}` };
    }
    if (!v.devBatOk) {
      return {
        ok: false,
        detail: `Dev bat missing. Expected: ${s.paths.devBat}`,
      };
    }
    // Human default only - NEVER append nullrhi / playtest / -unattended here.
    spawn("cmd.exe", ["/c", "start", "raceGPS Cleveland Race", s.paths.devBat], {
      detached: true,
      stdio: "ignore",
      cwd: path.dirname(s.paths.devBat),
    }).unref();
    return { ok: true, detail: `started ${s.paths.devBat}` };
  });

  ipcMain.handle("launch:workshop", () => ({
    ok: true,
    detail: "workshop - navigate renderer /workshop",
  }));
  ipcMain.handle("logs:open", async () => {
    const s = loadSettings(settingsPath());
    await shell.openPath(s.paths.logDir);
  });
  ipcMain.handle("workshop:cli", async () => ({
    code: 1,
    stdout: "",
    stderr: "workshop cli stub - Task 7",
  }));

  createWindow();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
