import { Link } from "react-router-dom";
import { ArrowLeft } from "./Icons";

export default function Header({ tool, release, desktop }) {
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
          <Link to="/" className="brand-link"><img className="brand-symbol" src="/vibehub-mark.svg" alt="" /><strong>VibeHub</strong><span className="brand-caption">工具合集</span></Link>
        )}
      </div>
      <div className="header-actions">
        {!desktop && release && <a className="btn-ghost desktop-download" href={release.download_url}>下载 Windows 版</a>}
      </div>
    </header>
  );
}
