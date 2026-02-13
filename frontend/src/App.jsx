import { Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Builder from "./pages/Builder";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/builder" element={<Builder />} />
      <Route path="/builder/:slug" element={<Builder />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
