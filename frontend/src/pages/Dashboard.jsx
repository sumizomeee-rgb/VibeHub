import ToolCard from "../components/ToolCard";

export default function Dashboard({ tools, loading, error, retry }) {
  return (
    <main className="launcher-home">
      <div className="home-content">
        <section className="home-intro">
          <div className="home-copy">
            <span className="home-eyebrow"><i /> VIBEHUB · DAILY TOOLS</span>
            <h1>顺手的小工具，<br /><em>都收在这里。</em></h1>
            <p>处理图片、裁切素材、转换文档。打开即用，完成后随时回到这里。</p>
          </div>
          <aside className="collection-stamp" aria-label={`当前收录 ${tools.length} 个工具`}>
            <span>CURATED</span>
            <strong>{loading ? "—" : String(tools.length).padStart(2, "0")}</strong>
            <small>件日常工具</small>
          </aside>
        </section>
        <div className="catalog-heading"><h2>工具目录</h2><span>选择一项开始</span></div>
        {error ? <div className="launcher-message" role="alert"><p>{error}</p><button className="btn-primary" onClick={retry}>重新加载</button></div>
          : loading ? <div className="tool-grid" aria-label="正在加载工具">{[0, 1, 2].map(n => <div className="launcher-card card-placeholder" key={n} />)}</div>
          : tools.length ? <div className="tool-grid">{tools.map((tool, index) => <ToolCard key={tool.id} tool={tool} index={index} />)}</div>
          : <div className="launcher-message">此版本暂未包含工具。</div>}
        <footer className="home-footer"><span>VibeHub</span><span>轻量、专注、随取随用</span></footer>
      </div>
    </main>
  );
}
