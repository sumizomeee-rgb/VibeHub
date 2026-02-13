import { useState } from "react";

export default function ToolCard({ tool, index, onAction }) {
  const [renaming, setRenaming] = useState(false);
  const [newName, setNewName] = useState(tool.display_name || tool.slug);

  const alive = tool.alive && tool.status === "active";
  const isError = tool.status === "error";
  const isStopped = !alive && !isError;

  const statusText = alive ? "运行中" : isError ? "异常" : "已停止";
  const statusColor = alive
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
      className="rounded-2xl p-5 flex flex-col gap-3 transition-all duration-200"
      style={{
        background: "var(--vh-surface)",
        border: "1px solid var(--vh-border)",
        boxShadow: "var(--vh-shadow-sm)",
        gridColumn: alive ? "span 2" : "span 1",
        animationDelay: `${index * 60}ms`,
      }}
    >
      {/* Header: name + status */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <span
            className="w-2.5 h-2.5 rounded-full flex-shrink-0"
            style={{
              background: statusColor,
              animation: alive ? "pulse-green 2s ease-in-out infinite" : "none",
            }}
          />
          {renaming ? (
            <div className="flex items-center gap-2">
              <input
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleRename()}
                className="px-2 py-1 rounded-lg text-sm outline-none"
                style={{
                  background: "var(--vh-bg-secondary)",
                  color: "var(--vh-text)",
                  border: "1px solid var(--vh-border)",
                }}
                autoFocus
              />
              <button onClick={handleRename} className="text-xs cursor-pointer" style={{ color: "var(--vh-primary)" }}>
                确定
              </button>
              <button onClick={() => setRenaming(false)} className="text-xs cursor-pointer" style={{ color: "var(--vh-text-muted)" }}>
                取消
              </button>
            </div>
          ) : (
            <>
              <span className="font-semibold" style={{ color: "var(--vh-text)", letterSpacing: "-0.02em" }}>
                {tool.display_name || tool.slug}
              </span>
              <button
                onClick={() => setRenaming(true)}
                className="text-xs cursor-pointer opacity-40 hover:opacity-100 transition-opacity"
                style={{ color: "var(--vh-text-muted)" }}
                title="重命名"
              >
                ✏️
              </button>
            </>
          )}
        </div>
        <span
          className="text-xs font-medium px-2.5 py-1 rounded-full"
          style={{
            color: statusColor,
            background: alive
              ? "rgba(5,150,105,0.1)"
              : isError
              ? "rgba(220,38,38,0.1)"
              : "rgba(161,161,170,0.1)",
          }}
        >
          {statusText}
        </span>
      </div>

      {/* Meta info */}
      <div className="flex items-center gap-4 text-xs" style={{ color: "var(--vh-text-muted)" }}>
        <span className="font-mono">/tools/{tool.slug}/</span>
        <span>{tool.created_at || "未知"}</span>
        {(tool.click_count || 0) > 0 && <span>{tool.click_count} 次使用</span>}
      </div>

      {/* Divider */}
      <div className="w-full h-px" style={{ background: "var(--vh-border)" }} />

      {/* Actions */}
      <div className="flex items-center gap-2">
        {alive && (
          <ActionBtn
            label="打开"
            onClick={() => {
              onAction("click", tool.slug);
              window.open(`/tools/${tool.slug}/`, "_blank");
            }}
          />
        )}
        <ActionBtn label="编辑" onClick={() => onAction("edit", tool.slug)} />
        <ActionBtn
          label="重启"
          color="var(--vh-warning)"
          onClick={() => onAction("restart", tool.slug)}
        />
        <div className="flex-1" />
        <ActionBtn
          label="🗑"
          color="var(--vh-error)"
          onClick={() => onAction("delete", tool.slug)}
        />
      </div>
    </div>
  );
}

function ActionBtn({ label, onClick, color }) {
  return (
    <button
      onClick={onClick}
      className="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors cursor-pointer"
      style={{
        color: color || "var(--vh-text-secondary)",
        background: "transparent",
        border: "none",
      }}
      onMouseEnter={(e) => (e.target.style.background = "var(--vh-bg-secondary)")}
      onMouseLeave={(e) => (e.target.style.background = "transparent")}
    >
      {label}
    </button>
  );
}
