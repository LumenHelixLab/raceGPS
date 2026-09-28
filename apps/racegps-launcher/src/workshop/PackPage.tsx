import { FormEvent, useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";
import { usePack } from "./PackContext";
import type { WorkshopOutletContext } from "./WorkshopLayout";

export function suggestedPackPath(worktreeRoot: string): string {
  const root = worktreeRoot.trim().replace(/[\\/]+$/, "");
  return `${root ? `${root}\\` : ""}Saved\\workshop-packs\\burke_overpass_proof_v1`;
}

export function PackPage() {
  const { packDir, setPackDir } = usePack();
  const { worktreeRoot } = useOutletContext<WorkshopOutletContext>();
  const suggestion = suggestedPackPath(worktreeRoot);
  const [draft, setDraft] = useState(packDir ?? "");

  useEffect(() => {
    setDraft(packDir ?? "");
  }, [packDir]);

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const next = draft.trim();
    setPackDir(next || null);
  }

  return (
    <section>
      <h1>Pack</h1>
      <p>{packDir ? `Pack open: ${packDir}` : "No pack open."}</p>
      <form className="form" onSubmit={onSubmit}>
        <label>
          Local pack directory
          <input
            type="text"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder={suggestion}
          />
        </label>
        <div className="row">
          <button type="submit">Open pack</button>
          <button type="button" onClick={() => setPackDir(null)}>
            Close pack
          </button>
        </div>
      </form>
      <p>
        Suggested output path: <code>{suggestion}</code>
      </p>
    </section>
  );
}
