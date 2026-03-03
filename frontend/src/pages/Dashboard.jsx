import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header";
import ToolCard from "../components/ToolCard";
import P5Background from "../components/P5Background";
import { Search, Sparkles, BarChart, Clock } from "../components/Icons";
import { fetchTools, deleteTool, renameTool, restartTool, clickTool, stopTool, startTool } from "../api/tools";

const SORT_OPTIONS = [
  { label: "创建时间", value: "created_at", icon: Clock },
  { label: "名称", value: "display_name", icon: null },
  { label: "使用量", value: "click_count", icon: BarChart },
];

export default function Dashboard() {
  const [tools, setTools] = useState([]);
  const [search, setSearch] = useState("");
  const [sortValue, setSortValue] = useState("created_at");
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);
  const [restartingSlug, setRestartingSlug] = useState(null);
  const [stoppingSlug, setStoppingSlug] = useState(null);
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

  let filtered = tools;
  if (search.trim()) {
    const q = search.toLowerCase();
    filtered = filtered.filter(
      (t) =>
        (t.display_name || "").toLowerCase().includes(q) ||
        t.slug.toLowerCase().includes(q)
    );
  }

  filtered = [...filtered].sort((a, b) => {
    if (sortValue === "display_name") return (a.display_name || "").localeCompare(b.display_name || "");
    if (sortValue === "click_count") return (b.click_count || 0) - (a.click_count || 0);
    return (b.created_at || "").localeCompare(a.created_at || "");
  });

  const runningCount = tools.filter((t) => t.alive && t.status === "active").length;

  async function handleAction(action, slug, extra) {
    try {
      if (action === "delete") {
        await deleteTool(slug);
        setToast({ type: "success", message: "删除成功" });
      } else if (action === "rename") {
        await renameTool(slug, extra);
        setToast({ type: "success", message: "重命名成功" });
      } else if (action === "restart") {
        setRestartingSlug(slug);
        await restartTool(slug);
        setRestartingSlug(null);
        setToast({ type: "success", message: "重启成功" });
      } else if (action === "stop") {
        setStoppingSlug(slug);
        await stopTool(slug);
        setStoppingSlug(null);
        setToast({ type: "success", message: "已停止" });
      } else if (action === "start") {
        setRestartingSlug(slug);
        await startTool(slug);
        setRestartingSlug(null);
        setToast({ type: "success", message: "启动成功" });
      } else if (action === "click") {
        await clickTool(slug);
      } else if (action === "edit") {
        navigate(`/builder/${slug}`);
        return;
      }
      await loadTools();
    } catch (e) {
      console.error(`操作失败 [${action}]:`, e);
      setToast({ type: "error", message: `操作失败: ${e.message}` });
    }
  }

  return (
    <div className="min-h-screen relative" style={{ background: "transparent" }}>
      <P5Background />
      <Header onRefresh={loadTools} />

      {toast && <Toast toast={toast} onClose={() => setToast(null)} />}

      <div className="max-w-6xl mx-auto px-6 pt-8 pb-4 relative z-10">
        {/* Stats + Search bar */}
        <div className="flex items-center gap-4 mb-8">
          {/* Stats chips */}
          {!loading && tools.length > 0 && (
            <div className="hidden md:flex items-center gap-2 mr-2">
              <span
                className="status-badge"
                style={{ background: "var(--vh-bg-secondary)", color: "var(--vh-text-secondary)" }}
              >
                {tools.length} 个工具
              </span>
              {runningCount > 0 && (
                <span
                  className="status-badge"
                  style={{ background: "rgba(var(--vh-accent-rgb), 0.1)", color: "var(--vh-success)" }}
                >
                  <span
                    className="w-1.5 h-1.5 rounded-full inline-block"
                    style={{ background: "var(--vh-success)" }}
                  />
                  {runningCount} 运行中
                </span>
              )}
            </div>
          )}

          <div className="flex-1" />

          {/* Search */}
          <div className="relative" style={{ width: 240 }}>
            <span
              className="absolute left-3 top-1/2 -translate-y-1/2"
              style={{ color: "var(--vh-text-muted)" }}
            >
              <Search size={15} />
            </span>
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="搜索工具..."
              className="input-field"
              style={{ paddingLeft: 34, fontSize: 13 }}
            />
          </div>

          {/* Sort */}
          <select
            value={sortValue}
            onChange={(e) => setSortValue(e.target.value)}
            className="input-field"
            style={{ width: "auto", fontSize: 13, cursor: "pointer", paddingRight: 28 }}
          >
            {SORT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 pb-12 relative z-10">
        {loading ? (
          <LoadingSkeleton />
        ) : filtered.length === 0 && !search ? (
          <EmptyState />
        ) : filtered.length === 0 && search ? (
          <div className="text-center py-20 animate-fade-in relative z-10">
            <div className="mb-3" style={{ color: "var(--vh-text-muted)" }}>
              <Search size={40} />
            </div>
            <div className="text-lg font-medium" style={{ color: "var(--vh-text-secondary)" }}>
              没有找到匹配的工具
            </div>
            <div className="text-sm mt-1.5" style={{ color: "var(--vh-text-muted)" }}>
              搜索 "{search}" 无结果
            </div>
          </div>
        ) : (
          <div
            className="w-full gap-5"
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(3, 1fr)",
            }}
          >
            {filtered.map((tool, i) => (
              <ToolCard
                key={tool.slug}
                tool={tool}
                index={i}
                onAction={handleAction}
                restarting={restartingSlug === tool.slug}
                stopping={stoppingSlug === tool.slug}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-24 animate-fade-in">
      <div
        className="w-24 h-24 rounded-3xl flex items-center justify-center mb-8"
        style={{
          background: "linear-gradient(135deg, rgba(var(--vh-primary-rgb), 0.12), rgba(var(--vh-primary-rgb), 0.03))",
          boxShadow: "0 8px 32px rgba(var(--vh-primary-rgb), 0.08)",
        }}
      >
        <Sparkles size={40} style={{ color: "var(--vh-primary)" }} />
      </div>
      <div className="text-2xl font-bold mb-2" style={{ color: "var(--vh-text)", letterSpacing: "-0.02em" }}>
        还没有部署任何工具
      </div>
      <div className="text-sm mb-8" style={{ color: "var(--vh-text-muted)", maxWidth: 320, textAlign: "center", lineHeight: 1.6 }}>
        描述你想要的工具，AI 帮你自动生成代码、测试并一键上线
      </div>
      <a href="/builder" className="btn-primary" style={{ padding: "12px 28px", fontSize: 15 }}>
        <Sparkles size={16} />
        创建第一个工具
      </a>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div
      className="w-full gap-5"
      style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)" }}
    >
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className="animate-fade-in"
          style={{
            animationDelay: `${i * 100}ms`,
            background: "var(--vh-surface)",
            border: "1px solid var(--vh-border)",
            borderRadius: "var(--vh-radius)",
            padding: 20,
            height: 140,
          }}
        >
          <div
            style={{
              width: "60%",
              height: 14,
              borderRadius: 6,
              background: "linear-gradient(90deg, var(--vh-bg-secondary) 25%, var(--vh-bg-tertiary) 50%, var(--vh-bg-secondary) 75%)",
              backgroundSize: "200% 100%",
              animation: "shimmer 1.5s infinite",
            }}
          />
          <div
            style={{
              width: "40%",
              height: 10,
              borderRadius: 5,
              marginTop: 12,
              background: "linear-gradient(90deg, var(--vh-bg-secondary) 25%, var(--vh-bg-tertiary) 50%, var(--vh-bg-secondary) 75%)",
              backgroundSize: "200% 100%",
              animation: "shimmer 1.5s infinite",
              animationDelay: "0.2s",
            }}
          />
        </div>
      ))}
    </div>
  );
}

function Toast({ toast, onClose }) {
  const { type, message } = toast;
  const bgColor = type === "success" ? "var(--vh-success)" : type === "error" ? "var(--vh-error)" : "var(--vh-primary)";

  useState(() => {
    const timer = setTimeout(onClose, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div
      className="animate-fade-in"
      style={{
        position: "fixed",
        top: 80,
        right: 24,
        zIndex: 9999,
        background: bgColor,
        color: "#fff",
        padding: "12px 20px",
        borderRadius: 10,
        fontSize: 14,
        fontWeight: 500,
        boxShadow: "0 4px 16px rgba(0,0,0,0.15)",
      }}
    >
      {message}
    </div>
  );
}
