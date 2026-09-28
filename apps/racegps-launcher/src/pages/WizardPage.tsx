import { FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { LauncherSettings, RaceMode } from "@racegps/launcher-settings";

type WizardPageProps = {
  onCompleted?: (settings: LauncherSettings) => void;
};

export function WizardPage({ onCompleted }: WizardPageProps) {
  const navigate = useNavigate();
  const [current, setCurrent] = useState<LauncherSettings | null>(null);
  const [packageExe, setPackageExe] = useState("");
  const [devBat, setDevBat] = useState("");
  const [workshopPython, setWorkshopPython] = useState("");
  const [worktreeRoot, setWorktreeRoot] = useState("");
  const [gpuNote, setGpuNote] = useState("");
  const [raceMode, setRaceMode] = useState<RaceMode>("package");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void window.racegps
      .getSettings()
      .then((s) => {
        setCurrent(s);
        setPackageExe(s.paths.packageExe);
        setDevBat(s.paths.devBat);
        setWorkshopPython(s.paths.workshopPython);
        setWorktreeRoot(s.paths.worktreeRoot);
        setGpuNote(s.gpuNote);
        setRaceMode(s.raceMode);
      })
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : String(err)),
      );
  }, []);

  async function onFinish(e: FormEvent) {
    e.preventDefault();
    if (!current) return;
    setSaving(true);
    setError(null);
    try {
      const next: LauncherSettings = {
        ...current,
        paths: {
          ...current.paths,
          packageExe,
          devBat,
          workshopPython,
          worktreeRoot,
        },
        gpuNote,
        raceMode,
        firstRunCompleted: true,
      };
      await window.racegps.saveSettings(next);
      onCompleted?.(next);
      navigate("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSaving(false);
    }
  }

  if (error && !current) {
    return (
      <main className="page">
        <h1>First-run wizard</h1>
        <p className="error">{error}</p>
      </main>
    );
  }

  if (!current) {
    return (
      <main className="page">
        <p>Loading settings…</p>
      </main>
    );
  }

  return (
    <main className="page">
      <h1>First-run wizard</h1>
      <p>Confirm paths and race mode for Easy Test Beta.</p>
      <form className="form" onSubmit={onFinish}>
        <label>
          Race package exe path
          <input
            value={packageExe}
            onChange={(e) => setPackageExe(e.target.value)}
            required
          />
        </label>
        <label>
          Dev bat path
          <input value={devBat} onChange={(e) => setDevBat(e.target.value)} required />
        </label>
        <label>
          Workshop python path
          <input
            value={workshopPython}
            onChange={(e) => setWorkshopPython(e.target.value)}
            required
          />
        </label>
        <label>
          Worktree root
          <input
            value={worktreeRoot}
            onChange={(e) => setWorktreeRoot(e.target.value)}
            required
          />
        </label>
        <label>
          GPU / adapter note
          <input
            value={gpuNote}
            onChange={(e) => setGpuNote(e.target.value)}
            placeholder="e.g. RTX 4070"
          />
        </label>
        <fieldset>
          <legend>Package vs Dev default</legend>
          <label className="radio">
            <input
              type="radio"
              name="raceMode"
              checked={raceMode === "package"}
              onChange={() => setRaceMode("package")}
            />
            Package (awaiting build until cook unlock)
          </label>
          <label className="radio">
            <input
              type="radio"
              name="raceMode"
              checked={raceMode === "dev"}
              onChange={() => setRaceMode("dev")}
            />
            Dev (LaunchClevelandRace.bat)
          </label>
        </fieldset>
        {error ? <p className="error">{error}</p> : null}
        <button type="submit" disabled={saving}>
          {saving ? "Saving…" : "Finish"}
        </button>
      </form>
    </main>
  );
}
