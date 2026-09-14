import { useEffect, useState } from "react";
import { fetchTool, openTool } from "../api/tools";

/** One host for every tool, in browsers and WebView2. Hidden hosts stay mounted. */
export default function ToolHost({ tool, active }) {
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState({ status: "starting", message: "正在准备工具…" });
  const [loaded, setLoaded] = useState(false);
  const [frameFailed, setFrameFailed] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    let timer;
    setLoaded(false);
    setFrameFailed(false);
    setState({ status: "starting", message: "正在打开工具…" });
    const update = async (first = false) => {
      try {
        const next = await (first ? openTool(tool.id, controller.signal) : fetchTool(tool.id, controller.signal));
        if (controller.signal.aborted) return;
        setState(next);
        if (next.status === "starting") timer = setTimeout(() => update(), 800);
      } catch (error) {
        if (error.name !== "AbortError") setState({ status: "error", message: error.message });
      }
    };
    update(true);
    return () => { controller.abort(); clearTimeout(timer); };
  }, [tool.id, attempt]);

  // Probe the child only when the user returns to it. A crashed tool is retryable;
  // an already loaded, healthy iframe is never reloaded on normal navigation.
  useEffect(() => {
    if (!active || state.status !== "ready") return;
    const controller = new AbortController();
    fetchTool(tool.id, controller.signal).then(next => {
      if (next.status === "error") setState(next);
    }).catch(() => {});
    return () => controller.abort();
  }, [active, tool.id, state.status]);

  const failed = state.status === "error" || frameFailed;
  const retry = () => setAttempt(n => n + 1);

  return (
    <section className="tool-workspace" hidden={!active} aria-label={tool.name}>
      {state.status === "ready" && !frameFailed && <iframe
        key={attempt} title={tool.name} src={tool.url} className="tool-frame"
        allow="clipboard-read; clipboard-write" onLoad={(event) => {
          // Caddy errors after readiness must not look like a successfully loaded tool.
          const doc = event.currentTarget.contentDocument;
          if (doc && !doc.body?.textContent?.trim() && !doc.querySelector("canvas,img,input")) setFrameFailed(true);
          else setLoaded(true);
        }} onError={() => setFrameFailed(true)}
      />}
      {(!loaded || failed) && <div className="tool-status" role={failed ? "alert" : "status"}>
        {!failed && <span className="launcher-spinner" />}
        <h2>{failed ? "暂时无法打开工具" : tool.name}</h2>
        <p>{failed ? (state.message || "工具页面加载失败，请重试。") : state.message || "正在加载页面…"}</p>
        {failed && <button className="btn-primary" onClick={retry}>重新打开</button>}
      </div>}
    </section>
  );
}
