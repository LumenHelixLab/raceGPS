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
import { runPythonModule } from "./workshopCli";

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

function writeWorkshopCliLog(
  logDir: string,
  argv: string[],
  result: { code: number; stdout: string; stderr: string },
): string {
  fs.mkdirSync(logDir, { recursive: true });
  const stamp = new Date().toISOString().replace(/[:.]/g, "-");
  const logPath = path.join(logDir, `workshop-cli-${stamp}.log`);
  const body = [
    `argv: ${JSON.stringify(argv)}`,
    `code: ${result.code}`,
    "----- stdout -----",
    result.stdout,
    "----- stderr -----",
    result.stderr,
    "",
  ].join("\n");
  fs.writeFileSync(logPath, body, "utf8");
  return logPath;
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
  ipcMain.handle("shell:openPath", async (_e, target: string) => {
    if (!target || typeof target !== "string") {
      return { ok: false, detail: "No path provided." };
    }
    const err = await shell.openPath(target);
    if (err) {
      return { ok: false, detail: err };
    }
    return { ok: true, detail: target };
  });
  ipcMain.handle("workshop:cli", async (_e, argv: string[]) => {
    const s = loadSettings(settingsPath());
    if (!Array.isArray(argv) || argv.length === 0) {
      const fail = {
        code: 1,
        stdout: "",
        stderr: "workshop:cli requires a non-empty argv array.",
        logPath: "",
      };
      return fail;
    }
    if (!fs.existsSync(s.paths.workshopPython)) {
      return {
        code: 1,
        stdout: "",
        stderr: `workshopPython missing: ${s.paths.workshopPython}`,
        logPath: s.paths.logDir,
      };
    }
    const result = await runPythonModule({
      python: s.paths.workshopPython,
      worktreeRoot: s.paths.worktreeRoot,
      argv,
    });
    let logPath = s.paths.logDir;
    try {
      logPath = writeWorkshopCliLog(s.paths.logDir, argv, result);
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      result.stderr = `${result.stderr}${result.stderr ? "\n" : ""}log write failed: ${msg}`;
    }
    return { ...result, logPath };
  });

  createWindow();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
