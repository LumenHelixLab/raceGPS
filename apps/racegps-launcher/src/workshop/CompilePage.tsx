import { usePack } from "./PackContext";

export function CompilePage() {
  const { packDir } = usePack();

  return (
    <section>
      <h1>Compile</h1>
      <p>
        {packDir
          ? `No compile run yet for ${packDir}.`
          : "No pack open. Compile is unavailable until a pack is selected."}
      </p>
    </section>
  );
}
