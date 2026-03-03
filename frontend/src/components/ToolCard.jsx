import { useState } from "react";
import { ExternalLink, Edit3, RotateCw, Trash2, Check, X, Globe, Clock } from "./Icons";

export default function ToolCard({ tool, index, onAction, restarting, stopping }) {
  const [renaming, setRenaming] = useState(false);
  const [newName, setNewName] = useState(tool.display_name || tool.slug);
  const [hovered, setHovered] = useState(false);

  const alive = tool.alive && tool.status === "active";
  const isError = tool.status === "error";

  const formatDate = (dateStr) => dateStr ? dateStr.slice(5) : "";

  const statusText = stopping ? "停止中" : restarting ? "重启中" : alive ? "运行中" : isError ? "异常" : "已停止";
  const statusColor = stopping
    ? "var(--vh-text-muted)"
    : restarting
    ? "var(--vh-warning)"
    : alive
    ? "var(--vh-success)"
    : isError
    ? "var(--vh-error)"
    : "var(--vh-text-muted)";

  async function handleRename() {
    if (!newName.trim()) return;
    await onAction("rename", tool.slug, newName.trim());
    setRenaming(false);
  }

  return (
    <div
      className="card p-5 flex flex-col gap-3.5 animate-fade-in-scale"
      style={{
        gridColumn: alive ? "span 2" : "span 1",
        animationDelay: `${index * 50}ms`,
        position: "relative",
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* 重启遮罩层 */}
      {restarting && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: "rgba(255, 255, 255, 0.95)",
            backdropFilter: "blur(4px)",
            borderRadius: "var(--vh-radius)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: "12px",
            zIndex: 10,
          }}
        >
          <RotateCw
            size={28}
            style={{
              color: "var(--vh-warning)",
              animation: "spin 1s linear infinite",
            }}
          />
          <span style={{ color: "var(--vh-text-secondary)", fontSize: 14, fontWeight: 500 }}>
            重启中...
          </span>
        </div>
      )}

      {/* 停止遮罩层 */}
      {stopping && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: "rgba(255, 255, 255, 0.95)",
            backdropFilter: "blur(4px)",
            borderRadius: "var(--vh-radius)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: "12px",
            zIndex: 10,
          }}
        >
          <svg width="28" height="28" viewBox="0 0 24 24" fill="var(--vh-text-muted)">
            <rect x="6" y="6" width="12" height="12" rx="2" />
          </svg>
          <span style={{ color: "var(--vh-text-secondary)", fontSize: 14, fontWeight: 500 }}>
            停止中...
          </span>
        </div>
      )}

      {/* Header row */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3 min-w-0">
          {/* Status dot */}
          <div className="relative flex-shrink-0">
            <span
              className="block w-2.5 h-2.5 rounded-full"
              style={{
                background: statusColor,
                animation: alive ? "pulse-green 2s ease-in-out infinite" : "none",
              }}
            />
          </div>

          {/* Name */}
          {renaming ? (
            <div className="flex items-center gap-2">
              <input
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleRename();
                  if (e.key === "Escape") setRenaming(false);
                }}
                className="input-field"
                style={{ padding: "4px 10px", fontSize: 13, width: 160 }}
                autoFocus
              />
              <button onClick={handleRename} className="btn-ghost" style={{ padding: 4, color: "var(--vh-success)" }}>
                <Check size={15} />
              </button>
              <button onClick={() => setRenaming(false)} className="btn-ghost" style={{ padding: 4, color: "var(--vh-text-muted)" }}>
                <X size={15} />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <span
                className="font-semibold truncate"
                style={{ color: "var(--vh-text)", fontSize: 15, letterSpacing: "-0.02em" }}
              >
                {tool.display_name || tool.slug}
              </span>
              <button
                className="btn-ghost"
                style={{ padding: 4, opacity: hovered ? 1 : 0, transition: "opacity 0.2s" }}
                onClick={() => setRenaming(true)}
                disabled={restarting || stopping}
                title="重命名"
              >
                <Edit3 size={14} style={{ color: "var(--vh-text-muted)" }} />
              </button>
            </div>
          )}
        </div>

        {/* Status badge */}
        <span
          className="status-badge flex-shrink-0"
          style={{
            color: statusColor,
            background: alive
              ? "rgba(var(--vh-accent-rgb), 0.1)"
              : isError
              ? "rgba(220,38,38,0.08)"
              : "var(--vh-bg-secondary)",
          }}
        >
          <span
            className="w-1.5 h-1.5 rounded-full"
            style={{ background: statusColor, display: "inline-block" }}
          />
          {statusText}
        </span>
      </div>

      {/* Meta */}
      <div className="flex items-center gap-3 text-xs" style={{ color: "var(--vh-text-muted)" }}>
        <span className="flex items-center gap-1">
          <Globe size={12} />
          <span style={{ fontFamily: "var(--vh-font-mono)", fontSize: 11 }}>{tool.slug}</span>
        </span>
        {tool.created_at && (
          <span className="flex items-center gap-1">
            <Clock size={12} />
            {formatDate(tool.created_at)}
          </span>
        )}
        {(tool.click_count || 0) > 0 && (
          <span>{tool.click_count} 次使用</span>
        )}
      </div>

      {/* 弹性占位，将按钮推到底部 */}
      <div className="flex-1" />

      {/* Divider */}
      <div className="w-full h-px" style={{ background: "var(--vh-border)" }} />

      {/* Actions */}
      <div className="flex items-center gap-1">
        {alive && (
          <a
            className="btn-ghost"
            style={{ fontSize: 12, padding: "5px 10px", textDecoration: "none", display: "inline-flex", alignItems: "center", gap: "4px" }}
            href={`/tools/${tool.slug}/`}
            target="_blank"
            rel="noopener noreferrer"
            onClick={() => {
              onAction("click", tool.slug);
            }}
          >
            <ExternalLink size={14} /> 打开
          </a>
        )}
        <button
          className="btn-ghost"
          style={{ fontSize: 12, padding: "5px 10px" }}
          onClick={() => onAction("edit", tool.slug)}
          disabled={restarting || stopping}
        >
          <Edit3 size={14} /> 编辑
        </button>
        {alive ? (
          <button
            className="btn-ghost"
            style={{ fontSize: 12, padding: "5px 10px", color: "var(--vh-text-muted)" }}
            onClick={() => onAction("stop", tool.slug)}
            disabled={restarting || stopping}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="6" y="6" width="12" height="12" rx="2" />
            </svg>
            停止
          </button>
        ) : (
          <button
            className="btn-ghost"
            style={{ fontSize: 12, padding: "5px 10px", color: "var(--vh-success)" }}
            onClick={() => onAction("start", tool.slug)}
            disabled={restarting || stopping}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="5 3 19 12 5 21 5 3" />
            </svg>
            启动
          </button>
        )}
        <button
          className="btn-ghost"
          style={{ fontSize: 12, padding: "5px 10px", color: "var(--vh-warning)" }}
          onClick={() => onAction("restart", tool.slug)}
          disabled={restarting || stopping}
        >
          <RotateCw size={14} /> 重启
        </button>
        <div className="flex-1" />
        <button
          className="btn-ghost"
          style={{
            padding: "5px 8px",
            color: "var(--vh-error)",
            opacity: hovered ? 1 : 0.4,
            transition: "opacity 0.2s",
          }}
          onClick={() => onAction("delete", tool.slug)}
          disabled={restarting || stopping}
        >
          <Trash2 size={14} />
        </button>
      </div>
    </div>
  );
}
