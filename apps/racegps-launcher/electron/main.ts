import { app, BrowserWindow, ipcMain, shell } from "electron";
import path from "node:path";
import {
  loadSettings,
  resetSettings,
  saveSettings,
  settingsFilePath,
  type LauncherSettings,
} from "@racegps/launcher-settings";

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
  // launch/validate stubs filled in Task 4
  ipcMain.handle("paths:validate", () => ({ stub: true }));
  ipcMain.handle("launch:race", () => ({
    ok: false,
    detail: "launch stub - wire in Task 4",
  }));
  ipcMain.handle("launch:workshop", () => ({
    ok: true,
    detail: "workshop stub - navigate renderer /workshop",
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

