import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Header from "../components/Header";
import ProgressStepper from "../components/ProgressStepper";
import LogConsole from "../components/LogConsole";
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

  // 编辑模式：加载现有代码
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

      <div className="max-w-3xl mx-auto p-8 flex flex-col gap-6">
        {/* Title */}
        {!result && (
          <TitleSection editSlug={editSlug} />
        )}

        {/* Success panel */}
        {result && (
          <SuccessPanel result={result} navigate={navigate} />
        )}

        {/* Form (hidden on success) */}
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
          <div className="animate-fade-in">
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
            className="p-4 rounded-xl text-sm"
            style={{
              background: "rgba(220,38,38,0.08)",
              color: "var(--vh-error)",
              border: "1px solid rgba(220,38,38,0.15)",
            }}
          >
            ❌ {error}
          </div>
        )}

        {/* Deploy button */}
        {!result && (
          <button
            onClick={handleDeploy}
            disabled={building || !prompt.trim()}
            className="w-full py-3.5 rounded-xl text-base font-medium text-white transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
              background: building
                ? "var(--vh-text-muted)"
                : "var(--vh-primary)",
              border: "none",
            }}
          >
            {building ? "⏳ 部署中..." : "🚀 开始部署"}
          </button>
        )}
      </div>
    </div>
  );
}

function TitleSection({ editSlug }) {
  return (
    <div className="flex items-center gap-3 animate-fade-in">
      <div
        className="w-11 h-11 rounded-xl flex items-center justify-center"
        style={{
          background: editSlug
            ? "linear-gradient(135deg, rgba(251,191,36,0.15), rgba(251,191,36,0.05))"
            : "linear-gradient(135deg, rgba(129,140,248,0.15), rgba(129,140,248,0.05))",
        }}
      >
        <span className="text-xl">{editSlug ? "✏️" : "✨"}</span>
      </div>
      <div>
        <h1 className="text-2xl font-bold m-0" style={{ color: "var(--vh-text)", letterSpacing: "-0.02em" }}>
          {editSlug ? `编辑 ${editSlug}` : "创建新工具"}
        </h1>
        <p className="text-sm m-0 mt-0.5" style={{ color: "var(--vh-text-muted)" }}>
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
        className="rounded-2xl p-5"
        style={{
          background: "var(--vh-surface)",
          border: "1px solid var(--vh-border)",
        }}
      >
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder={
            editSlug
              ? "描述需要修改或新增的功能..."
              : "例如：做一个 JSON 格式化工具，支持压缩和美化..."
          }
          rows={4}
          className="w-full resize-none outline-none text-sm leading-relaxed"
          style={{
            background: "transparent",
            color: "var(--vh-text)",
            border: "none",
            fontFamily: "var(--vh-font-sans)",
          }}
        />
      </div>

      {existingCode && (
        <div>
          <button
            onClick={() => setShowCode(!showCode)}
            className="text-sm cursor-pointer flex items-center gap-1"
            style={{ color: "var(--vh-text-secondary)", background: "none", border: "none" }}
          >
            {showCode ? "▼" : "▶"} 查看当前代码
          </button>
          {showCode && (
            <pre
              className="mt-2 p-4 rounded-xl overflow-auto text-xs"
              style={{
                background: "var(--vh-bg-secondary)",
                color: "var(--vh-text-secondary)",
                fontFamily: "var(--vh-font-mono)",
                maxHeight: 320,
                border: "1px solid var(--vh-border)",
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
      className="rounded-2xl p-10 flex flex-col items-center gap-5 animate-fade-in"
      style={{
        background: "linear-gradient(135deg, rgba(5,150,105,0.08), var(--vh-surface))",
        border: "1px solid rgba(5,150,105,0.15)",
      }}
    >
      <div
        className="w-20 h-20 rounded-2xl flex items-center justify-center"
        style={{
          background: "linear-gradient(135deg, #059669, #34d399)",
          boxShadow: "0 8px 32px rgba(52,211,153,0.35)",
        }}
      >
        <span className="text-4xl text-white">✓</span>
      </div>
      <div className="text-2xl font-bold" style={{ color: "var(--vh-success)" }}>
        {result.display_name}
      </div>
      <div className="text-lg font-medium" style={{ color: "var(--vh-accent)" }}>
        部署成功，工具已上线
      </div>
      <div className="flex items-center gap-4 mt-2 flex-wrap justify-center">
        <a
          href={result.url}
          target="_blank"
          rel="noreferrer"
          className="px-7 py-3 rounded-xl text-sm font-medium text-white no-underline"
          style={{ background: "var(--vh-accent)" }}
        >
          立即体验
        </a>
        <button
          onClick={() => navigate("/")}
          className="px-5 py-3 rounded-xl text-sm font-medium cursor-pointer"
          style={{
            color: "var(--vh-text-secondary)",
            background: "transparent",
            border: "1px solid var(--vh-border)",
          }}
        >
          返回看板
        </button>
        <button
          onClick={() => navigate("/builder")}
          className="px-5 py-3 rounded-xl text-sm font-medium cursor-pointer"
          style={{
            color: "var(--vh-text-secondary)",
            background: "transparent",
            border: "1px solid var(--vh-border)",
          }}
        >
          再建一个
        </button>
      </div>
    </div>
  );
}
