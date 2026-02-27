import { useState, useEffect, useRef } from "react";
import { Link, useLocation } from "react-router-dom";
import { Zap, Plus, Moon, Sun, ArrowLeft, RefreshCw, Settings, Hammer, Power } from "./Icons";
import { rebuildFrontend, restartBackend } from "../api/admin";

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
          <AdminMenu />

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

function AdminMenu() {
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState(null);
  const [confirmConfig, setConfirmConfig] = useState(null);
  const ref = useRef(null);

  useEffect(() => {
    function handleClick(e) {
      if (confirmConfig) return; // 有二次弹窗时不关闭菜单
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [confirmConfig]);

  async function executeRebuild() {
    setConfirmConfig(null);
    setStatus("rebuilding");
    try {
      await rebuildFrontend();
      setStatus("rebuild-ok");
      setTimeout(() => { setStatus(null); setOpen(false); }, 1500);
    } catch (e) {
      setStatus("rebuild-err");
      setTimeout(() => setStatus(null), 3000);
    }
  }

  function handleRebuild() {
    setConfirmConfig({
      title: "编译前端",
      content: "确定要重新编译前端资源吗？这可能需要一小段时间。",
      onConfirm: executeRebuild
    });
  }

  async function executeRestart() {
    setConfirmConfig(null);
    setStatus("restarting");
    try {
      await restartBackend();
      setStatus("restart-ok");
    } catch {
      // 后端已退出，连接断开是正常的
      setStatus("restart-ok");
    }
  }

  function handleRestart() {
    setConfirmConfig({
      title: "重启后端",
      content: "确定要重启后端服务器吗？所有工具将短暂不可用。",
      onConfirm: executeRestart
    });
  }

  const btnStyle = {
    display: "flex", alignItems: "center", gap: 8,
    width: "100%", padding: "10px 14px", border: "none",
    background: "transparent", cursor: "pointer",
    fontSize: 13, color: "var(--vh-text-secondary)",
    borderRadius: 8, transition: "background 0.15s",
  };

  return (
    <div ref={ref} style={{ position: "relative" }}>
      <button
        onClick={() => setOpen(!open)}
        className="btn-ghost"
        style={{ padding: "8px" }}
        title="管理"
      >
        <Settings size={18} style={{ color: "var(--vh-text-secondary)" }} />
      </button>

      {open && (
        <div
          className="animate-fade-in"
          style={{
            position: "absolute", right: 0, top: "calc(100% + 8px)",
            background: "var(--vh-surface)",
            border: "1px solid var(--vh-border)",
            borderRadius: 12, padding: 6, minWidth: 200,
            boxShadow: "0 8px 32px rgba(0,0,0,0.12)",
            zIndex: 100,
          }}
        >
          <button
            style={btnStyle}
            onMouseEnter={(e) => e.currentTarget.style.background = "var(--vh-bg-secondary)"}
            onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
            onClick={handleRebuild}
            disabled={status === "rebuilding"}
          >
            <Hammer size={15} />
            {status === "rebuilding" ? "重建中..." : status === "rebuild-ok" ? "重建完成" : "重建前端"}
          </button>
          <button
            style={btnStyle}
            onMouseEnter={(e) => e.currentTarget.style.background = "var(--vh-bg-secondary)"}
            onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
            onClick={handleRestart}
            disabled={!!status}
          >
            <Power size={15} />
            {status === "restarting" ? "重启中..." : status === "restart-ok" ? "已发送重启" : "重启后端"}
          </button>
        </div>
      )}

      {/* 自定义非原生弹窗 */}
      {confirmConfig && (
        <div
          style={{
            position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: "rgba(0,0,0,0.5)",
            backdropFilter: "blur(4px)",
            display: "flex", alignItems: "center", justifyContent: "center",
            zIndex: 9999
          }}
          className="animate-fade-in"
          onClick={(e) => e.stopPropagation()} // 防止点击穿透触发关闭
        >
          <div
            className="card animate-fade-in-scale flex flex-col gap-4"
            style={{
              width: 360, maxWidth: "90vw", padding: 24,
              background: "var(--vh-surface)",
              border: "1px solid var(--vh-border)",
              boxShadow: "0 24px 48px rgba(0,0,0,0.2)"
            }}
          >
            <div style={{ fontSize: 18, fontWeight: 600, color: "var(--vh-text)" }}>
              {confirmConfig.title}
            </div>
            <div style={{ fontSize: 14, color: "var(--vh-text-secondary)", lineHeight: 1.5 }}>
              {confirmConfig.content}
            </div>
            <div className="flex justify-end gap-3 mt-2">
              <button
                className="btn-ghost"
                style={{ padding: "8px 16px" }}
                onClick={() => setConfirmConfig(null)}
              >
                取消
              </button>
              <button
                className="btn-primary"
                style={{ padding: "8px 16px" }}
                onClick={confirmConfig.onConfirm}
              >
                确定
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
