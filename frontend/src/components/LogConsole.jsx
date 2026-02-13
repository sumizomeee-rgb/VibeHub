import { useEffect, useRef } from "react";

export default function LogConsole({ logs }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <div className="w-full rounded-xl overflow-hidden" style={{ border: "1px solid var(--vh-border)" }}>
      {/* Terminal header */}
      <div
        className="flex items-center gap-2 px-4 py-2"
        style={{ background: "var(--vh-bg-secondary)" }}
      >
        <span className="w-3 h-3 rounded-full" style={{ background: "#ff5f57" }} />
        <span className="w-3 h-3 rounded-full" style={{ background: "#febc2e" }} />
        <span className="w-3 h-3 rounded-full" style={{ background: "#28c840" }} />
        <span className="text-xs font-medium ml-2" style={{ color: "var(--vh-text-muted)" }}>
          部署日志
        </span>
      </div>

      {/* Log content */}
      <div
        className="p-4 overflow-y-auto"
        style={{
          background: "var(--vh-bg-secondary)",
          fontFamily: "var(--vh-font-mono)",
          fontSize: "13px",
          lineHeight: "1.6",
          maxHeight: 320,
          color: "var(--vh-text-secondary)",
        }}
      >
        {logs.length === 0 && (
          <div style={{ color: "var(--vh-text-muted)" }}>等待构建开始...</div>
        )}
        {logs.map((line, i) => (
          <div
            key={i}
            style={{
              color: line.includes("❌")
                ? "var(--vh-error)"
                : line.includes("✅")
                ? "var(--vh-success)"
                : line.includes("⚠️")
                ? "var(--vh-warning)"
                : "var(--vh-text-secondary)",
            }}
          >
            {line}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
