import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import type { LauncherSettings, RaceMode } from "@racegps/launcher-settings";
import { useSettings } from "../lib/useSettings";

export function SettingsPage() {
  const navigate = useNavigate();
  const { settings, loading, error, save, reset } = useSettings();
  const [draft, setDraft] = useState<LauncherSettings | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (settings) setDraft({ ...settings, paths: { ...settings.paths } });
  }, [settings]);

  async function onSave(e: FormEvent) {
    e.preventDefault();
    if (!draft) return;
    setBusy(true);
    setStatus(null);
    try {
      await save(draft);
      setStatus("Saved.");
    } catch (err) {
      setStatus(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  async function onReset() {
    setBusy(true);
    setStatus(null);
    try {
      const next = await reset();
      setDraft({ ...next, paths: { ...next.paths } });
      setStatus("Reset to defaults.");
      if (!next.firstRunCompleted) navigate("/wizard");
    } catch (err) {
      setStatus(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  async function onRevealLogs() {
    setStatus(null);
    try {
      await window.racegps.openLogs();
    } catch (err) {
      setStatus(err instanceof Error ? err.message : String(err));
    }
  }

  function setPath(
    key: keyof LauncherSettings["paths"],
    value: string,
  ) {
    setDraft((prev) =>
      prev
        ? { ...prev, paths: { ...prev.paths, [key]: value } }
        : prev,
    );
  }

  function setRaceMode(mode: RaceMode) {
    setDraft((prev) => (prev ? { ...prev, raceMode: mode } : prev));
  }

  if (loading || !draft) {
    return (
      <main className="page">
        <p>Loading settings…</p>
      </main>
    );
  }

  return (
    <main className="page">
      <h1>Settings</h1>
      <p>
        <Link to="/">← Home</Link>
      </p>
      {error ? <p className="error">{error}</p> : null}
      <form className="form" onSubmit={onSave}>
        <fieldset>
          <legend>Race mode</legend>
          <label className="radio">
            <input
              type="radio"
              name="raceMode"
              checked={draft.raceMode === "package"}
              onChange={() => setRaceMode("package")}
            />
            Package (awaiting build)
          </label>
          <label className="radio">
            <input
              type="radio"
              name="raceMode"
              checked={draft.raceMode === "dev"}
              onChange={() => setRaceMode("dev")}
            />
            Dev
          </label>
        </fieldset>
        <label>
          Worktree root
          <input
            value={draft.paths.worktreeRoot}
            onChange={(e) => setPath("worktreeRoot", e.target.value)}
            required
          />
        </label>
        <label>
          Dev bat
          <input
            value={draft.paths.devBat}
            onChange={(e) => setPath("devBat", e.target.value)}
            required
          />
        </label>
        <label>
          Package exe
          <input
            value={draft.paths.packageExe}
            onChange={(e) => setPath("packageExe", e.target.value)}
            required
          />
        </label>
        <label>
          Workshop python
          <input
            value={draft.paths.workshopPython}
            onChange={(e) => setPath("workshopPython", e.target.value)}
            required
          />
        </label>
        <label>
          Uproject
          <input
            value={draft.paths.uproject}
            onChange={(e) => setPath("uproject", e.target.value)}
            required
          />
        </label>
        <label>
          Log dir
          <input
            value={draft.paths.logDir}
            onChange={(e) => setPath("logDir", e.target.value)}
            required
          />
        </label>
        <label>
          GPU / adapter note
          <input
            value={draft.gpuNote}
            onChange={(e) =>
              setDraft((prev) =>
                prev ? { ...prev, gpuNote: e.target.value } : prev,
              )
            }
          />
        </label>
        {status ? <p className="status">{status}</p> : null}
        <div className="row">
          <button type="submit" disabled={busy}>
            Save
          </button>
          <button type="button" disabled={busy} onClick={() => void onRevealLogs()}>
            Reveal logs
          </button>
          <button type="button" disabled={busy} onClick={() => void onReset()}>
            Reset defaults
          </button>
        </div>
      </form>
    </main>
  );
}
