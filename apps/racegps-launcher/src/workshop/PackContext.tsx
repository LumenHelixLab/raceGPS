import { createContext, useContext, useMemo, useState, type PropsWithChildren } from "react";

export type PackState = {
  packDir: string | null;
  setPackDir: (p: string | null) => void;
};

type PackProviderProps = PropsWithChildren;

export const PackContext = createContext<PackState | null>(null);

export function PackProvider({ children }: PackProviderProps) {
  const [packDir, setPackDir] = useState<string | null>(null);
  const value = useMemo(() => ({ packDir, setPackDir }), [packDir]);

  return <PackContext.Provider value={value}>{children}</PackContext.Provider>;
}

export function usePack(): PackState {
  const context = useContext(PackContext);
  if (!context) {
    throw new Error("usePack must be used within a PackProvider");
  }
  return context;
}
