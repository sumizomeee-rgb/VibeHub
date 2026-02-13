import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header";
import ToolCard from "../components/ToolCard";
import { fetchTools, deleteTool, renameTool, restartTool, clickTool } from "../api/tools";

const SORT_OPTIONS = {
  "创建时间": "created_at",
  "名称": "display_name",
  "使用量": "click_count",
};

export default function Dashboard() {
  const [tools, setTools] = useState([]);
  const [search, setSearch] = useState("");
  const [sortKey, setSortKey] = useState("创建时间");
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const loadTools = useCallback(async () => {
    try {
      const data = await fetchTools();
      setTools(data);
    } catch (e) {
      console.error("加载工具列表失败:", e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTools();
  }, [loadTools]);

  // 过滤 + 排序
  let filtered = tools;
  if (search.trim()) {
    const q = search.toLowerCase();
    filtered = filtered.filter(
      (t) =>
        (t.display_name || "").toLowerCase().includes(q) ||
        t.slug.toLowerCase().includes(q)
    );
  }

  const sk = SORT_OPTIONS[sortKey] || "created_at";
  filtered = [...filtered].sort((a, b) => {
    if (sk === "display_name") return (a.display_name || "").localeCompare(b.display_name || "");
    if (sk === "click_count") return (b.click_count || 0) - (a.click_count || 0);
    return (b.created_at || "").localeCompare(a.created_at || "");
  });

  async function handleAction(action, slug, extra) {
    try {
      if (action === "delete") {
        await deleteTool(slug);
      } else if (action === "rename") {
        await renameTool(slug, extra);
      } else if (action === "restart") {
        await restartTool(slug);
      } else if (action === "click") {
        await clickTool(slug);
      } else if (action === "edit") {
        navigate(`/builder/${slug}`);
        return;
      }
      await loadTools();
    } catch (e) {
      console.error(`操作失败 [${action}]:`, e);
    }
  }

  return (
    <div className="min-h-screen" style={{ background: "var(--vh-bg)" }}>
      <Header onRefresh={loadTools} />

      <div className="max-w-5xl mx-auto px-8 pt-8 pb-4">
        {/* Search + Sort bar */}
        <div className="flex items-center gap-4 mb-6">
          <div className="flex-1 relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sm" style={{ color: "var(--vh-text-muted)" }}>
              🔍
            </span>
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="搜索工具..."
              className="w-full pl-9 pr-4 py-2.5 rounded-xl text-sm outline-none transition-shadow"
              style={{
                background: "var(--vh-surface)",
                color: "var(--vh-text)",
                border: "1px solid var(--vh-border)",
              }}
            />
          </div>
          <select
            value={sortKey}
            onChange={(e) => setSortKey(e.target.value)}
            className="px-3 py-2.5 rounded-xl text-sm outline-none cursor-pointer"
            style={{
              background: "var(--vh-surface)",
              color: "var(--vh-text)",
              border: "1px solid var(--vh-border)",
            }}
          >
            {Object.keys(SORT_OPTIONS).map((k) => (
              <option key={k} value={k}>{k}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-8 pb-8">
        {loading ? (
          <div className="text-center py-20" style={{ color: "var(--vh-text-muted)" }}>
            加载中...
          </div>
        ) : filtered.length === 0 && !search ? (
          <EmptyState />
        ) : filtered.length === 0 && search ? (
          <div className="text-center py-16 animate-fade-in">
            <div className="text-4xl mb-4">🔍</div>
            <div className="text-lg font-medium" style={{ color: "var(--vh-text-secondary)" }}>
              没有找到匹配的工具
            </div>
            <div className="text-sm mt-1" style={{ color: "var(--vh-text-muted)" }}>
              搜索 "{search}" 无结果
            </div>
          </div>
        ) : (
          <div
            className="w-full gap-8"
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(3, 1fr)",
            }}
          >
            {filtered.map((tool, i) => (
              <ToolCard key={tool.slug} tool={tool} index={i} onAction={handleAction} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-20 animate-fade-in">
      <div
        className="w-20 h-20 rounded-2xl flex items-center justify-center mb-6"
        style={{
          background: "linear-gradient(135deg, rgba(79,70,229,0.1), rgba(79,70,229,0.03))",
        }}
      >
        <span className="text-4xl">✨</span>
      </div>
      <div className="text-xl font-semibold" style={{ color: "var(--vh-text)" }}>
        还没有部署任何工具
      </div>
      <div className="text-sm mt-2" style={{ color: "var(--vh-text-muted)" }}>
        描述你想要的工具，AI 帮你生成并一键上线
      </div>
      <a
        href="/builder"
        className="mt-6 px-6 py-3 rounded-xl text-sm font-medium text-white no-underline"
        style={{ background: "var(--vh-primary)" }}
      >
        创建第一个工具
      </a>
    </div>
  );
}
