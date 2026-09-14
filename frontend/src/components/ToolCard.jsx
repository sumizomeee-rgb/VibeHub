import { Link } from "react-router-dom";

function ToolIcon({ kind }) {
  const paths = {
    avatar: <><circle cx="12" cy="8" r="3" /><path d="M5 21v-2a7 7 0 0 1 14 0v2" /></>,
    crop: <><path d="M6 3v13a2 2 0 0 0 2 2h13M3 6h13a2 2 0 0 1 2 2v13" /></>,
    image: <><rect x="3" y="3" width="18" height="18" rx="3" /><circle cx="8" cy="8" r="1.5" /><path d="m3 17 5-5 4 4 3-3 6 6" /></>,
    pdf: <><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z" /><path d="M14 2v6h6M8 13h8M8 17h5" /></>,
    pages: <><rect x="8" y="3" width="13" height="16" rx="2" /><path d="M4 7H3v14h13v-1M12 8h5M12 12h5" /></>,
    tool: <><rect x="3" y="3" width="7" height="7" rx="2" /><rect x="14" y="3" width="7" height="7" rx="2" /><rect x="3" y="14" width="7" height="7" rx="2" /><rect x="14" y="14" width="7" height="7" rx="2" /></>,
  };
  return <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[kind] || paths.tool}</svg>;
}

export default function ToolCard({ tool }) {
  return (
    <Link to={`/tool/${tool.id}`} data-tool-card={tool.id} className="launcher-card">
      <span className="tool-icon"><ToolIcon kind={tool.icon} /></span>
      <h2>{tool.name}</h2>
      <p>{tool.description}</p>
      <span className="tool-enter">打开工具 <span aria-hidden="true">↗</span></span>
    </Link>
  );
}
