import { useEffect, useRef } from "react";
import { Terminal } from "./Icons";

export default function LogConsole({ logs }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <div
      className="w-full overflow-hidden"
      style={{
        borderRadius: "var(--vh-radius)",
        border: "1px solid var(--vh-border)",
        boxShadow: "var(--vh-shadow-sm)",
      }}
    >
      {/* Terminal header */}
      <div
        className="flex items-center gap-2.5 px-4 py-2.5"
        style={{ background: "var(--vh-bg-tertiary)", borderBottom: "1px solid var(--vh-border)" }}
      >
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full" style={{ background: "#ff5f57" }} />
          <span className="w-3 h-3 rounded-full" style={{ background: "#febc2e" }} />
          <span className="w-3 h-3 rounded-full" style={{ background: "#28c840" }} />
        </div>
        <div className="flex items-center gap-1.5 ml-2" style={{ color: "var(--vh-text-muted)" }}>
          <Terminal size={13} />
          <span className="text-xs font-medium">部署日志</span>
        </div>
      </div>

      {/* Log content */}
      <div
        className="p-4 overflow-y-auto"
        style={{
          background: "var(--vh-bg-secondary)",
          fontFamily: "var(--vh-font-mono)",
          fontSize: 12,
          lineHeight: 1.7,
          maxHeight: 340,
          color: "var(--vh-text-secondary)",
        }}
      >
        {logs.length === 0 && (
          <div className="flex items-center gap-2" style={{ color: "var(--vh-text-muted)" }}>
            <span className="animate-spin inline-block" style={{ width: 12, height: 12, border: "2px solid var(--vh-border-strong)", borderTopColor: "var(--vh-primary)", borderRadius: "50%" }} />
            等待构建开始...
          </div>
        )}
        {logs.map((line, i) => (
          <div
            key={i}
            className="animate-slide-in-right"
            style={{
              animationDelay: `${Math.min(i * 20, 200)}ms`,
              color: line.includes("❌") || line.includes("FAIL") || line.includes("Error")
                ? "var(--vh-error)"
                : line.includes("✅") || line.includes("PASS") || line.includes("成功")
                ? "var(--vh-success)"
                : line.includes("⚠️") || line.includes("WARN")
                ? "var(--vh-warning)"
                : "var(--vh-text-secondary)",
            }}
          >
            <span style={{ color: "var(--vh-text-muted)", userSelect: "none" }}>
              {String(i + 1).padStart(3, " ")}  </span>{line}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
