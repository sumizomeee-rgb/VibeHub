async function request(path, { signal, ...options } = {}) {
  const response = await fetch(path, {
    ...options,
    signal,
    headers: { "X-VibeHub-Request": "1", ...options.headers },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || `请求失败 (${response.status})`);
  return data;
}

export const fetchTools = (signal) => request("/api/tools", { signal });
export const fetchApp = (signal) => request("/api/app", { signal });
export const openTool = (id, signal) => request(`/api/tools/${encodeURIComponent(id)}/open`, { method: "POST", signal });
export const fetchTool = (id, signal) => request(`/api/tools/${encodeURIComponent(id)}`, { signal });
export async function fetchDesktopRelease(signal) {
  const response = await fetch("/api/desktop/latest", { signal });
  if (response.status === 404) return null;
  if (!response.ok) throw new Error("无法读取客户端发布信息");
  return response.json();
}
