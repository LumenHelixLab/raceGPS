import { Navigate, Route, Routes } from "react-router-dom";
import { PlaceholderHome } from "./pages/PlaceholderHome";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<PlaceholderHome />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
