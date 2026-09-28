import { usePack } from "./PackContext";

export function ValidatePage() {
  const { packDir } = usePack();

  return (
    <section>
      <h1>Validate</h1>
      <p>
        {packDir
          ? `No validation run yet for ${packDir}.`
          : "No pack open. Validation is unavailable until a pack is selected."}
      </p>
    </section>
  );
}
