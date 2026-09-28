import { useState } from "react";
import { usePack } from "./PackContext";

export function ExportPage() {
  const { packDir } = usePack();
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onReveal() {
    setError(null);
    setStatus(null);
    if (!packDir?.trim()) {
      setError("No pack open. Export a pack on Compile first.");
      return;
    }
    try {
      const result = await window.racegps.openPath(packDir);
      if (!result.ok) {
        setError(result.detail || "Failed to open pack folder.");
        return;
      }
      setStatus(`Opened: ${packDir}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  async function onCopy() {
    setError(null);
    setStatus(null);
    if (!packDir?.trim()) {
      setError("No pack open. Export a pack on Compile first.");
      return;
    }
    try {
      await navigator.clipboard.writeText(packDir);
      setStatus("Pack path copied to clipboard.");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  return (
    <section>
      <h1>Export</h1>
      <p>
        {packDir
          ? `Pack folder: ${packDir}`
          : "No pack open. Export is unavailable until a pack is selected."}
      </p>
      <p>Race .rgpack load is later — export proof only.</p>
      <p>Package mode is awaiting build until cook is unlocked.</p>
      <div className="row">
        <button type="button" disabled={!packDir} onClick={() => void onReveal()}>
          Reveal pack folder
        </button>
        <button type="button" disabled={!packDir} onClick={() => void onCopy()}>
          Copy pack path
        </button>
      </div>
      {error ? <p className="error">{error}</p> : null}
      {status ? <p>{status}</p> : null}
    </section>
  );
}
