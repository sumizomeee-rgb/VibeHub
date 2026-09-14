import ToolCard from "../components/ToolCard";
import P5Background from "../components/P5Background";

export default function Dashboard({ tools, loading, error, retry }) {
  return (
    <main className="launcher-home">
      <P5Background />
      <div className="home-content">
        <div className="home-intro"><span className="home-eyebrow">YOUR EVERYDAY TOOLKIT</span><h1>选一个工具，开始使用。</h1><p>处理图片、裁切素材、转换文档，都在这里。</p></div>
        {error ? <div className="launcher-message" role="alert"><p>{error}</p><button className="btn-primary" onClick={retry}>重新加载</button></div>
          : loading ? <div className="tool-grid" aria-label="正在加载工具">{[0, 1, 2].map(n => <div className="launcher-card card-placeholder" key={n} />)}</div>
          : tools.length ? <div className="tool-grid">{tools.map(tool => <ToolCard key={tool.id} tool={tool} />)}</div>
          : <div className="launcher-message">此版本暂未包含工具。</div>}
      </div>
    </main>
  );
}
