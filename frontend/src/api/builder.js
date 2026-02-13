const API_BASE = "/api";

export async function startBuild(prompt, editSlug = null) {
  const body = { prompt };
  if (editSlug) body.edit_slug = editSlug;

  const res = await fetch(`${API_BASE}/build`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "构建启动失败");
  }
  return res.json();
}
