import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { Zap, Plus, Moon, Sun, ArrowLeft, RefreshCw } from "./Icons";

export default function Header({ onRefresh }) {
  const location = useLocation();
  const [theme, setTheme] = useState(
    () => localStorage.getItem("vh-theme") || "light"
  );

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, []);

  function toggleTheme() {
    const next = theme === "light" ? "dark" : "light";
    document.documentElement.dataset.theme = next;
    localStorage.setItem("vh-theme", next);
    setTheme(next);
  }

  const isDashboard = location.pathname === "/";

  return (
    <header className="glass sticky top-0 z-50 border-b" style={{ borderColor: "var(--vh-border)" }}>
      <div className="max-w-6xl mx-auto flex items-center justify-between px-6 h-16">
        {/* Left: Logo */}
        <div className="flex items-center gap-4">
          <Link to="/" className="flex items-center gap-2.5 no-underline group">
            <div
              className="w-9 h-9 rounded-xl flex items-center justify-center"
              style={{
                background: "linear-gradient(135deg, var(--vh-primary), var(--vh-primary-dark))",
                boxShadow: "0 2px 8px rgba(var(--vh-primary-rgb), 0.3)",
              }}
            >
              <Zap size={18} style={{ color: "#fff" }} strokeWidth={2} />
            </div>
            <span
              className="text-lg font-bold tracking-tight"
              style={{ color: "var(--vh-text)" }}
            >
              VibeHub
            </span>
          </Link>
          <div className="hidden sm:flex items-center gap-2 ml-1">
            <div className="w-px h-5" style={{ background: "var(--vh-border-strong)" }} />
            <span className="text-xs font-medium tracking-wide uppercase" style={{ color: "var(--vh-text-muted)" }}>
              AI 工具工坊
            </span>
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={toggleTheme}
            className="btn-ghost"
            style={{ padding: "8px" }}
            title={theme === "light" ? "深色模式" : "浅色模式"}
          >
            {theme === "light"
              ? <Moon size={18} style={{ color: "var(--vh-text-secondary)" }} />
              : <Sun size={18} style={{ color: "var(--vh-text-secondary)" }} />
            }
          </button>

          {isDashboard && onRefresh && (
            <button
              onClick={onRefresh}
              className="btn-ghost"
              style={{ padding: "8px" }}
              title="刷新"
            >
              <RefreshCw size={18} style={{ color: "var(--vh-text-secondary)" }} />
            </button>
          )}

          {isDashboard ? (
            <Link to="/builder" className="btn-primary ml-1.5" style={{ padding: "8px 16px" }}>
              <Plus size={16} />
              <span>新建工具</span>
            </Link>
          ) : (
            <Link to="/" className="btn-ghost ml-1">
              <ArrowLeft size={16} />
              <span>返回看板</span>
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
