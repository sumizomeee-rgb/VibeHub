import { useEffect, useState } from "react";
import { Link, matchPath, useLocation } from "react-router-dom";
import { fetchApp, fetchDesktopRelease, fetchTools } from "./api/tools";
import Header from "./components/Header";
import ToolHost from "./components/ToolHost";
import Dashboard from "./pages/Dashboard";

export default function App() {
  const { pathname } = useLocation();
  const [tools, setTools] = useState([]);
  const [app, setApp] = useState({ desktop: false });
  const [release, setRelease] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reload, setReload] = useState(0);
  const [visited, setVisited] = useState([]);
  const route = matchPath("/tool/:id", pathname);
  const activeId = route?.params.id;
  const activeTool = tools.find(tool => tool.id === activeId);
  const home = pathname === "/";

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true); setError("");
    Promise.all([fetchTools(controller.signal), fetchApp(controller.signal)])
      .then(([list, info]) => { setTools(list); setApp(info); })
      .catch(e => { if (e.name !== "AbortError") setError(e.message); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    fetchDesktopRelease(controller.signal).then(setRelease).catch(() => {});
    return () => controller.abort();
  }, [reload]);

  useEffect(() => {
    if (activeTool) setVisited(old => old.includes(activeTool.id) ? old : [...old, activeTool.id]);
  }, [activeTool]);

  useEffect(() => { document.title = activeTool ? `${activeTool.name} · VibeHub` : "VibeHub"; }, [activeTool]);

  return <div className="launcher-app">
    <Header tool={!home ? (activeTool || { name: "工具" }) : null} release={release} desktop={app.desktop} />
    {home && <Dashboard tools={tools} loading={loading} error={error} retry={() => setReload(n => n + 1)} />}
    {!home && !activeTool && <div className="launcher-message"><h1>{loading ? "正在加载…" : error || "没有找到这个工具"}</h1><Link className="btn-primary" to="/">返回首页</Link></div>}
    {visited.map(id => {
      const tool = tools.find(t => t.id === id);
      return tool && <ToolHost key={id} tool={tool} active={id === activeId} />;
    })}
  </div>;
}
