const STEPS = ["审核需求", "生成代码", "单元测试", "启动服务", "注册路由", "完成"];

export default function ProgressStepper({ currentStep }) {
  return (
    <div className="flex items-center w-full gap-0">
      {STEPS.map((label, i) => {
        const isDone = i < currentStep;
        const isActive = i === currentStep;
        const isPending = i > currentStep;

        return (
          <div key={i} className="flex items-center" style={{ flex: 1 }}>
            {i > 0 && (
              <div
                className="h-0.5 flex-1 transition-colors duration-300"
                style={{
                  background: isDone
                    ? "var(--vh-success)"
                    : isActive
                    ? "var(--vh-primary)"
                    : "var(--vh-border)",
                }}
              />
            )}
            <div className="flex flex-col items-center gap-1" style={{ minWidth: 56 }}>
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300"
                style={{
                  background: isDone
                    ? "var(--vh-success)"
                    : isActive
                    ? "var(--vh-primary)"
                    : "var(--vh-bg-secondary)",
                  color: isDone || isActive ? "#fff" : "var(--vh-text-muted)",
                  boxShadow: isActive ? "var(--vh-shadow-glow)" : "none",
                }}
              >
                {isDone ? "✓" : i + 1}
              </div>
              <span
                className="text-xs font-medium whitespace-nowrap"
                style={{
                  color: isDone
                    ? "var(--vh-success)"
                    : isActive
                    ? "var(--vh-primary)"
                    : "var(--vh-text-muted)",
                }}
              >
                {label}
              </span>
            </div>
            {i < STEPS.length - 1 && i > 0 ? null : i === 0 ? null : null}
          </div>
        );
      })}
    </div>
  );
}
