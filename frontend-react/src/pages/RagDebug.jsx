import { useState } from 'react'
import { ragSearch } from '../api'

export default function RagDebug() {
  const [query, setQuery] = useState('')
  const [topK, setTopK] = useState(5)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)

  const search = async () => {
    if (!query) return
    setLoading(true)
    try { const r = await ragSearch(query, topK); setResults(r.data) }
    catch { setResults(null) }
    finally { setLoading(false) }
  }

  return (
    <div>
      <div className="page-header">
        <h1>🔍 RAG Knowledge Base Debug</h1>
        <p>Query the ChromaDB vector store and inspect retrieved chunks with similarity scores</p>
      </div>

      <div className="search-row">
        <input className="input-wide" value={query} onChange={e => setQuery(e.target.value)}
          placeholder="e.g. GDPR data portability, SLA credit calculation, refund policy…"
          onKeyDown={e => e.key === 'Enter' && search()} />
        <label style={{fontSize:'0.825rem',color:'var(--text-muted)',display:'flex',alignItems:'center',gap:6}}>
          Top K <input type="number" value={topK} min={1} max={10} onChange={e => setTopK(Number(e.target.value))} style={{width:56}} />
        </label>
        <button onClick={search} disabled={loading}>
          {loading ? <><span className="spinner" /> Searching…</> : '🔍 Search'}
        </button>
      </div>

      {results && (
        results.results.length === 0
          ? <div className="empty"><div className="empty-icon">🗄️</div>No results. Make sure the KB is seeded with <code style={{background:'var(--surface2)',padding:'2px 6px',borderRadius:4}}>python rag/create_kb.py</code></div>
          : <>
              <div className="info-box" style={{marginBottom:12}}>Found <b>{results.results.length}</b> chunks for query: <i>"{results.query}"</i></div>
              {results.results.map(r => (
                <details key={r.rank} className="card" style={{marginBottom:8}}>
                  <summary>
                    <span className="chunk-rank">#{r.rank}</span>
                    <span className="chunk-source" style={{flex:1,marginLeft:8}}>📄 {r.source_doc}</span>
                    <span className="chunk-distance">dist: {r.similarity_distance}</span>
                  </summary>
                  <div className="card-body">
                    <p className="chunk-text">{r.chunk_text}</p>
                  </div>
                </details>
              ))}
            </>
      )}
    </div>
  )
}
