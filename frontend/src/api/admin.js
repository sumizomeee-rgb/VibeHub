const API_BASE = "/api";

export async function rebuildFrontend() {
  const res = await fetch(`${API_BASE}/admin/rebuild-frontend`, { method: "POST" });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "重建前端失败");
  }
  return res.json();
}

export async function restartBackend() {
  const res = await fetch(`${API_BASE}/admin/restart`, { method: "POST" });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "重启后端失败");
  }
  return res.json();
}
