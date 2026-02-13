import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Header from "../components/Header";
import ProgressStepper from "../components/ProgressStepper";
import LogConsole from "../components/LogConsole";
import { Sparkles, Edit3, Rocket, Check, ExternalLink, ArrowLeft, Code2, ChevronDown, Eye } from "../components/Icons";
import { startBuild } from "../api/builder";
import { fetchToolCode } from "../api/tools";
import { connectBuildWS } from "../ws/build";

export default function Builder() {
  const { slug: editSlug } = useParams();
  const navigate = useNavigate();

  const [prompt, setPrompt] = useState("");
  const [existingCode, setExistingCode] = useState("");
  const [building, setBuilding] = useState(false);
  const [step, setStep] = useState(-1);
  const [logs, setLogs] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (editSlug) {
      fetchToolCode(editSlug)
        .then((data) => setExistingCode(data.code || ""))
        .catch(() => {});
    }
  }, [editSlug]);

  const handleDeploy = useCallback(async () => {
    if (!prompt.trim()) return;
    setBuilding(true);
    setStep(-1);
    setLogs([]);
    setResult(null);
    setError(null);

    try {
      const { task_id } = await startBuild(prompt, editSlug || null);

      connectBuildWS(task_id, {
        onStep(s, msg) {
          setStep(s);
          setLogs((prev) => [...prev, msg]);
        },
        onLog(msg) {
          setLogs((prev) => [...prev, msg]);
        },
        onComplete(data) {
          setResult(data);
          setBuilding(false);
        },
        onError(msg) {
          setError(msg);
          setBuilding(false);
        },
      });
    } catch (e) {
      setError(e.message);
      setBuilding(false);
    }
  }, [prompt, editSlug]);

  return (
    <div className="min-h-screen" style={{ background: "var(--vh-bg)" }}>
      <Header />

      <div className="max-w-3xl mx-auto px-6 py-10 flex flex-col gap-7">
        {/* Title */}
        {!result && <TitleSection editSlug={editSlug} />}

        {/* Success panel */}
        {result && <SuccessPanel result={result} navigate={navigate} />}

        {/* Form */}
        {!result && (
          <FormSection
            prompt={prompt}
            setPrompt={setPrompt}
            editSlug={editSlug}
            existingCode={existingCode}
          />
        )}

        {/* Progress stepper */}
        {step >= 0 && (
          <div className="animate-fade-in" style={{ padding: "0 4px" }}>
            <ProgressStepper currentStep={result ? 6 : step} />
          </div>
        )}

        {/* Log console */}
        {logs.length > 0 && (
          <div className="animate-fade-in">
            <LogConsole logs={logs} />
          </div>
        )}

        {/* Error */}
        {error && !building && (
          <div
            className="p-4 rounded-xl text-sm animate-fade-in flex items-start gap-3"
            style={{
              background: "rgba(220,38,38,0.06)",
              color: "var(--vh-error)",
              border: "1px solid rgba(220,38,38,0.12)",
            }}
          >
            <span className="flex-shrink-0 mt-0.5" style={{ opacity: 0.7 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" /><line x1="15" y1="9" x2="9" y2="15" /><line x1="9" y1="9" x2="15" y2="15" />
              </svg>
            </span>
            <span>{error}</span>
          </div>
        )}

        {/* Deploy button */}
        {!result && (
          <button
            onClick={handleDeploy}
            disabled={building || !prompt.trim()}
            className="btn-primary w-full"
            style={{
              padding: "14px 24px",
              fontSize: 15,
              borderRadius: 14,
              background: building
                ? "var(--vh-text-muted)"
                : "linear-gradient(135deg, var(--vh-primary), var(--vh-primary-dark))",
              boxShadow: building
                ? "none"
                : "0 4px 16px rgba(var(--vh-primary-rgb), 0.3)",
            }}
          >
            {building ? (
              <>
                <span
                  className="animate-spin inline-block"
                  style={{
                    width: 16, height: 16,
                    border: "2px solid rgba(255,255,255,0.3)",
                    borderTopColor: "#fff",
                    borderRadius: "50%",
                  }}
                />
                部署中...
              </>
            ) : (
              <>
                <Rocket size={18} />
                开始部署
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
}

function TitleSection({ editSlug }) {
  return (
    <div className="flex items-center gap-4 animate-fade-in">
      <div
        className="w-12 h-12 rounded-2xl flex items-center justify-center flex-shrink-0"
        style={{
          background: editSlug
            ? "linear-gradient(135deg, rgba(251,191,36,0.15), rgba(251,191,36,0.05))"
            : "linear-gradient(135deg, rgba(var(--vh-primary-rgb), 0.15), rgba(var(--vh-primary-rgb), 0.05))",
          boxShadow: editSlug
            ? "0 4px 16px rgba(251,191,36,0.1)"
            : "0 4px 16px rgba(var(--vh-primary-rgb), 0.08)",
        }}
      >
        {editSlug
          ? <Edit3 size={22} style={{ color: "var(--vh-warning)" }} />
          : <Sparkles size={22} style={{ color: "var(--vh-primary)" }} />
        }
      </div>
      <div>
        <h1
          className="text-2xl font-bold m-0"
          style={{ color: "var(--vh-text)", letterSpacing: "-0.025em" }}
        >
          {editSlug ? `编辑 ${editSlug}` : "创建新工具"}
        </h1>
        <p className="text-sm m-0 mt-1" style={{ color: "var(--vh-text-muted)" }}>
          {editSlug ? "修改需求后重新部署" : "描述你想要的工具，AI 会自动生成、测试并部署"}
        </p>
      </div>
    </div>
  );
}

function FormSection({ prompt, setPrompt, editSlug, existingCode }) {
  const [showCode, setShowCode] = useState(false);

  return (
    <>
      <div
        className="card"
        style={{ padding: 0, overflow: "hidden" }}
      >
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder={
            editSlug
              ? "描述需要修改或新增的功能..."
              : "例如：做一个 JSON 格式化工具，支持压缩和美化..."
          }
          rows={5}
          className="w-full resize-none outline-none text-sm leading-relaxed"
          style={{
            background: "transparent",
            color: "var(--vh-text)",
            border: "none",
            fontFamily: "var(--vh-font-sans)",
            padding: "20px 24px",
          }}
        />
        <div
          className="flex items-center justify-between px-5 py-3"
          style={{ borderTop: "1px solid var(--vh-border)" }}
        >
          <span className="text-xs" style={{ color: "var(--vh-text-muted)" }}>
            {prompt.length > 0 ? `${prompt.length} 字` : "支持自然语言描述"}
          </span>
        </div>
      </div>

      {existingCode && (
        <div className="animate-fade-in">
          <button
            onClick={() => setShowCode(!showCode)}
            className="btn-ghost"
            style={{ fontSize: 13, padding: "6px 12px", gap: 4 }}
          >
            {showCode ? <Eye size={14} /> : <Code2 size={14} />}
            {showCode ? "隐藏当前代码" : "查看当前代码"}
            <ChevronDown
              size={14}
              style={{
                transform: showCode ? "rotate(180deg)" : "rotate(0)",
                transition: "transform 0.2s ease",
              }}
            />
          </button>
          {showCode && (
            <pre
              className="mt-2 p-5 overflow-auto text-xs animate-fade-in"
              style={{
                background: "var(--vh-bg-secondary)",
                color: "var(--vh-text-secondary)",
                fontFamily: "var(--vh-font-mono)",
                maxHeight: 320,
                border: "1px solid var(--vh-border)",
                borderRadius: "var(--vh-radius)",
                lineHeight: 1.7,
              }}
            >
              {existingCode}
            </pre>
          )}
        </div>
      )}
    </>
  );
}

function SuccessPanel({ result, navigate }) {
  return (
    <div
      className="card animate-fade-in-scale flex flex-col items-center gap-6"
      style={{
        padding: "48px 40px",
        background: "linear-gradient(135deg, rgba(var(--vh-accent-rgb), 0.06), var(--vh-surface))",
        borderColor: "rgba(var(--vh-accent-rgb), 0.12)",
      }}
    >
      <div
        className="w-20 h-20 rounded-2xl flex items-center justify-center"
        style={{
          background: "linear-gradient(135deg, #059669, #34d399)",
          boxShadow: "0 8px 32px rgba(52,211,153,0.35)",
        }}
      >
        <Check size={36} style={{ color: "#fff" }} strokeWidth={2.5} />
      </div>
      <div className="text-center">
        <div className="text-2xl font-bold mb-1.5" style={{ color: "var(--vh-text)", letterSpacing: "-0.02em" }}>
          {result.display_name}
        </div>
        <div className="text-base font-medium" style={{ color: "var(--vh-success)" }}>
          部署成功，工具已上线
        </div>
      </div>
      <div className="flex items-center gap-3 mt-2 flex-wrap justify-center">
        <a
          href={result.url}
          target="_blank"
          rel="noreferrer"
          className="btn-primary"
          style={{
            padding: "12px 28px",
            background: "linear-gradient(135deg, #059669, #34d399)",
            boxShadow: "0 4px 16px rgba(52,211,153,0.3)",
          }}
        >
          <ExternalLink size={16} />
          立即体验
        </a>
        <button onClick={() => navigate("/")} className="btn-outline">
          <ArrowLeft size={16} />
          返回看板
        </button>
        <button onClick={() => navigate("/builder")} className="btn-outline">
          <Sparkles size={16} />
          再建一个
        </button>
      </div>
    </div>
  );
}
