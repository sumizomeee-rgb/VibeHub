const API_BASE = "/api";

export async function fetchTools() {
  const res = await fetch(`${API_BASE}/tools`);
  if (!res.ok) throw new Error("获取工具列表失败");
  return res.json();
}

export async function fetchTool(slug) {
  const res = await fetch(`${API_BASE}/tools/${slug}`);
  if (!res.ok) throw new Error("获取工具详情失败");
  return res.json();
}

export async function deleteTool(slug) {
  const res = await fetch(`${API_BASE}/tools/${slug}`, { method: "DELETE" });
  if (!res.ok) throw new Error("删除工具失败");
  return res.json();
}

export async function renameTool(slug, newName) {
  const res = await fetch(`${API_BASE}/tools/${slug}/rename`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ display_name: newName }),
  });
  if (!res.ok) throw new Error("重命名失败");
  return res.json();
}

export async function startTool(slug) {
  const res = await fetch(`${API_BASE}/tools/${slug}/start`, { method: "POST" });
  if (!res.ok) throw new Error("启动失败");
  return res.json();
}

export async function stopTool(slug) {
  const res = await fetch(`${API_BASE}/tools/${slug}/stop`, { method: "POST" });
  if (!res.ok) throw new Error("停止失败");
  return res.json();
}

export async function restartTool(slug) {
  const res = await fetch(`${API_BASE}/tools/${slug}/restart`, { method: "POST" });
  if (!res.ok) throw new Error("重启失败");
  return res.json();
}

export async function clickTool(slug) {
  await fetch(`${API_BASE}/tools/${slug}/click`, { method: "POST" });
}

export async function fetchToolCode(slug) {
  const res = await fetch(`${API_BASE}/tools/${slug}/code`);
  if (!res.ok) throw new Error("获取代码失败");
  return res.json();
}

export async function fetchToolLogs(slug, tail = 50) {
  const res = await fetch(`${API_BASE}/tools/${slug}/logs?tail=${tail}`);
  if (!res.ok) throw new Error("获取日志失败");
  return res.json();
}
