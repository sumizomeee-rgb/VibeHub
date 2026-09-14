import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Moon, Sun, Zap } from "./Icons";

export default function Header({ tool, release, desktop }) {
  const [theme, setTheme] = useState(() => localStorage.getItem("vh-theme") || "light");
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("vh-theme", theme);
  }, [theme]);

  return (
    <header className="launcher-header">
      <div className="launcher-brand">
        {tool ? (
          <>
            <Link className="btn-ghost home-link" to="/"><ArrowLeft size={18} /> 返回首页</Link>
            <span className="header-divider" />
            <span className="tool-heading">{tool.name}</span>
          </>
        ) : (
          <Link to="/" className="brand-link"><span className="brand-symbol"><Zap size={19} /></span><strong>VibeHub</strong><span className="brand-caption">工具合集</span></Link>
        )}
      </div>
      <div className="header-actions">
        {!desktop && release && <a className="btn-ghost desktop-download" href={release.download_url}>Windows 客户端</a>}
        <button className="btn-ghost" title={theme === "light" ? "深色模式" : "浅色模式"} aria-label="切换主题" onClick={() => setTheme(theme === "light" ? "dark" : "light")}>
          {theme === "light" ? <Moon size={18} /> : <Sun size={18} />}
        </button>
      </div>
    </header>
  );
}
