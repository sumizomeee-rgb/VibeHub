export function connectBuildWS(taskId, { onStep, onLog, onComplete, onError, onHeartbeat }) {
  const proto = location.protocol === "https:" ? "wss:" : "ws:";
  const url = `${proto}//${location.host}/ws/build/${taskId}`;
  let ws = null;
  let closed = false;

  function stop() {
    closed = true;
    ws?.close();
  }

  function connect() {
    ws = new WebSocket(url);

    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);
        switch (msg.type) {
          case "step_change":
            onStep?.(msg.step, msg.message);
            break;
          case "log":
            onLog?.(msg.message);
            break;
          case "complete":
            onComplete?.(msg.data);
            stop();
            break;
          case "error":
            onError?.(msg.message);
            stop();
            break;
          case "heartbeat":
            onHeartbeat?.();
            break;
        }
      } catch {}
    };

    ws.onclose = () => {
      if (!closed) {
        setTimeout(connect, 2000);
      }
    };

    ws.onerror = () => {};
  }

  connect();

  return { close: stop };
}
