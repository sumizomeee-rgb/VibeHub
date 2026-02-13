import { useState } from "react";
import { Link, useLocation } from "react-router-dom";

export default function Header({ onRefresh }) {
  const location = useLocation();
  const [theme, setTheme] = useState(
    () => localStorage.getItem("vh-theme") || "light"
  );

  function toggleTheme() {
    const next = theme === "light" ? "dark" : "light";
    document.documentElement.dataset.theme = next;
    localStorage.setItem("vh-theme", next);
    setTheme(next);
  }

  return (
    <header
      className="sticky top-0 z-50 flex items-center justify-between px-6 h-14 border-b"
      style={{
        background: "var(--vh-surface)",
        borderColor: "var(--vh-border)",
        backdropFilter: "blur(12px)",
      }}
    >
      <div className="flex items-center gap-4">
        <Link to="/" className="flex items-center gap-2 no-underline">
          <span className="text-2xl">⚡</span>
          <span
            className="text-xl font-bold tracking-tight"
            style={{ color: "var(--vh-text)" }}
          >
            VibeHub
          </span>
        </Link>
        <div
          className="w-px h-6"
          style={{ background: "var(--vh-border)" }}
        />
        <span className="text-sm" style={{ color: "var(--vh-text-muted)" }}>
          AI 工具工坊
        </span>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg transition-colors cursor-pointer"
          style={{ color: "var(--vh-text-secondary)" }}
          title="切换主题"
        >
          {theme === "light" ? "🌙" : "☀️"}
        </button>

        {location.pathname === "/" && onRefresh && (
          <button
            onClick={onRefresh}
            className="p-2 rounded-lg transition-colors cursor-pointer"
            style={{ color: "var(--vh-text-secondary)" }}
            title="刷新"
          >
            🔄
          </button>
        )}

        {location.pathname === "/" ? (
          <Link
            to="/builder"
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium no-underline text-white transition-colors"
            style={{ background: "var(--vh-primary)" }}
          >
            ＋ 新建工具
          </Link>
        ) : (
          <Link
            to="/"
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm no-underline transition-colors"
            style={{ color: "var(--vh-text-secondary)" }}
          >
            ← 返回看板
          </Link>
        )}
      </div>
    </header>
  );
}
