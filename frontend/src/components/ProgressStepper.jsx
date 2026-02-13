import { Check } from "./Icons";

const STEPS = ["审核需求", "生成代码", "单元测试", "启动服务", "注册路由", "完成"];

export default function ProgressStepper({ currentStep }) {
  return (
    <div className="flex items-center w-full">
      {STEPS.map((label, i) => {
        const isDone = i < currentStep;
        const isActive = i === currentStep;

        return (
          <div key={i} className="flex items-center" style={{ flex: 1 }}>
            {/* Connector line */}
            {i > 0 && (
              <div
                className="h-0.5 flex-1 transition-all duration-500"
                style={{
                  background: isDone
                    ? "var(--vh-success)"
                    : isActive
                    ? `linear-gradient(90deg, var(--vh-success), var(--vh-primary))`
                    : "var(--vh-border)",
                  borderRadius: 1,
                }}
              />
            )}

            {/* Step node */}
            <div className="flex flex-col items-center gap-1.5" style={{ minWidth: 52 }}>
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-500"
                style={{
                  background: isDone
                    ? "var(--vh-success)"
                    : isActive
                    ? "linear-gradient(135deg, var(--vh-primary), var(--vh-primary-dark))"
                    : "var(--vh-bg-secondary)",
                  color: isDone || isActive ? "#fff" : "var(--vh-text-muted)",
                  boxShadow: isActive
                    ? "0 0 0 4px rgba(var(--vh-primary-rgb), 0.15), 0 2px 8px rgba(var(--vh-primary-rgb), 0.2)"
                    : isDone
                    ? "0 2px 6px rgba(var(--vh-accent-rgb), 0.2)"
                    : "none",
                  transform: isActive ? "scale(1.1)" : "scale(1)",
                }}
              >
                {isDone ? <Check size={14} strokeWidth={2.5} /> : i + 1}
              </div>
              <span
                className="text-xs font-medium whitespace-nowrap transition-colors duration-300"
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
          </div>
        );
      })}
    </div>
  );
}
