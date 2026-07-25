import { useState, useEffect } from 'react'
import { processAll, processEmail, dryRunEmail, gmailStatus, gmailSync } from '../api'

export default function BulkOperations() {
  const [bulkResult, setBulkResult] = useState(null)
  const [bulkLoading, setBulkLoading] = useState(false)
  const [emailId, setEmailId] = useState(1)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [mode, setMode] = useState(null)
  const [gmailAuth, setGmailAuth] = useState(null)
  const [syncResult, setSyncResult] = useState(null)
  const [syncLoading, setSyncLoading] = useState(false)
  const [maxResults, setMaxResults] = useState(50)
  const [markRead, setMarkRead] = useState(false)

  useEffect(() => {
    gmailStatus().then(r => setGmailAuth(r.data)).catch(() => {})
  }, [])

  const handleSync = async () => {
    setSyncLoading(true); setSyncResult(null)
    try { const r = await gmailSync(maxResults, markRead); setSyncResult(r.data) }
    catch (e) { setSyncResult({ error: e.response?.data?.detail || String(e) }) }
    finally { setSyncLoading(false) }
  }

  const handleBulk = async () => {
    setBulkLoading(true); setBulkResult(null)
    try { const r = await processAll(); setBulkResult(r.data) }
    catch (e) { setBulkResult({ error: String(e) }) }
    finally { setBulkLoading(false) }
  }

  const handle = async (fn, m) => {
    setLoading(true); setMode(m); setResult(null)
    try { const r = await fn(emailId); setResult(r.data) }
    catch (e) { setResult({ error: String(e) }) }
    finally { setLoading(false) }
  }

  return (
    <div>
      <div className="page-header">
        <h1>⚙️ Bulk Operations</h1>
        <p>Process emails individually or run the AI agent across the entire inbox</p>
      </div>

      <div className="card" style={{marginBottom:16}}>
        <h3>📬 Gmail Sync</h3>
        <p style={{color:'var(--text-muted)',fontSize:'0.875rem',margin:'8px 0 16px'}}>
          Pull unread emails from Gmail and ingest them into the CRM.
        </p>

        {gmailAuth && (
          <div className={gmailAuth.authenticated ? 'success-box' : gmailAuth.credentials_file ? 'info-box' : 'alert-box'} style={{marginBottom:14}}>
            {gmailAuth.authenticated
              ? '✅ Gmail authenticated — token.json found'
              : gmailAuth.credentials_file
              ? 'ℹ️ credentials.json found. Click Sync below — a browser window will open for Google sign-in to complete OAuth.'
              : <>⚠️ credentials.json not found. Place it in <code style={{background:'var(--surface2)',padding:'2px 6px',borderRadius:4}}>backend/</code> and restart the server.</>}
          </div>
        )}

        <div className="search-row" style={{marginBottom:16}}>
          <label style={{fontSize:'0.825rem',color:'var(--text-muted)',display:'flex',alignItems:'center',gap:8}}>
            Max emails <input type="number" value={maxResults} min={1} max={500}
              onChange={e => setMaxResults(Number(e.target.value))} style={{width:72}} />
          </label>
          <label style={{fontSize:'0.825rem',color:'var(--text-muted)',display:'flex',alignItems:'center',gap:8}}>
            <input type="checkbox" checked={markRead} onChange={e => setMarkRead(e.target.checked)} />
            Mark as read after sync
          </label>
        </div>

        <button onClick={handleSync} disabled={syncLoading || !gmailAuth?.credentials_file}>
          {syncLoading ? <><span className="spinner" /> Syncing Gmail…</> : '📬 Sync Gmail Inbox'}
        </button>

        {syncResult && (
          syncResult.error
            ? <div className="alert-box" style={{marginTop:12}}>⚠️ {syncResult.error}</div>
            : <div className="success-box" style={{marginTop:12}}>
                ✅ Ingested <b>{syncResult.ingested}</b> new emails &nbsp;·&nbsp;
                Skipped <b>{syncResult.skipped_duplicates}</b> duplicates &nbsp;·&nbsp;
                Fetched <b>{syncResult.total_fetched}</b> from Gmail
              </div>
        )}
      </div>

      <div className="card" style={{marginBottom:16}}>
        <h3>🚀 Process All Emails</h3>
        <p style={{color:'var(--text-muted)',fontSize:'0.875rem',margin:'8px 0 16px'}}>
          Runs the AI triage agent on every email in the database. Estimated time: 5–10 minutes.
        </p>
        <button onClick={handleBulk} disabled={bulkLoading} style={{minWidth:260}}>
          {bulkLoading ? <><span className="spinner" /> Processing all emails…</> : '▶️ Process All Emails with AI Agent'}
        </button>

        {bulkResult && (
          bulkResult.error
            ? <div className="alert-box" style={{marginTop:12}}>⚠️ {bulkResult.error}</div>
            : <div className="success-box" style={{marginTop:12}}>
                ✅ Processed <b>{bulkResult.processed}</b> / <b>{bulkResult.total}</b> emails
                {bulkResult.errors?.length > 0 && (
                  <details style={{marginTop:8}}>
                    <summary style={{cursor:'pointer',color:'#fdba74'}}>⚠️ {bulkResult.errors.length} errors</summary>
                    <pre className="json-box" style={{marginTop:8}}>{JSON.stringify(bulkResult.errors, null, 2)}</pre>
                  </details>
                )}
              </div>
        )}
      </div>

      <div className="card">
        <h3>🔢 Process Single Email</h3>
        <p style={{color:'var(--text-muted)',fontSize:'0.875rem',margin:'8px 0 16px'}}>
          Run the agent on a specific email by ID — live execution or dry-run planning mode.
        </p>
        <div className="search-row">
          <label style={{fontSize:'0.825rem',color:'var(--text-muted)',display:'flex',alignItems:'center',gap:8}}>
            Email ID <input type="number" value={emailId} min={1} onChange={e => setEmailId(Number(e.target.value))} style={{width:80}} />
          </label>
          <button onClick={() => handle(processEmail, 'live')} disabled={loading}>
            {loading && mode === 'live' ? <><span className="spinner" /> Running…</> : '🤖 Process (Live)'}
          </button>
          <button className="btn-secondary" onClick={() => handle(dryRunEmail, 'dry')} disabled={loading}>
            {loading && mode === 'dry' ? <><span className="spinner" /> Planning…</> : '🔍 Dry Run'}
          </button>
        </div>

        {result && (
          result.error
            ? <div className="alert-box">{result.error}</div>
            : <>
                {result.classification && (
                  <><h4 style={{margin:'12px 0 8px'}}>Classification</h4>
                  <pre className="json-box">{JSON.stringify(result.classification, null, 2)}</pre></>
                )}
                {result.reasoning_trace?.length > 0 && (
                  <><h4 style={{margin:'16px 0 8px'}}>🧠 Reasoning Trace</h4>
                  {result.reasoning_trace.map((s, i) => (
                    <div key={i} className="trace-step">
                      <div className="trace-header"><span className="trace-step-badge">Step {s.step}</span>{s.action}</div>
                      <p>💭 {s.thought}</p>
                      {s.observation && <p>👁 {s.observation}</p>}
                    </div>
                  ))}</>
                )}
                {result.draft_reply
                  ? <><h4 style={{margin:'16px 0 8px'}}>📝 Draft Reply</h4><textarea readOnly value={result.draft_reply} rows={5} style={{width:'100%'}} /></>
                  : result.classification && <div className="info-box" style={{marginTop:12}}>ℹ️ No auto-reply generated — critical, security, or legal category requires human review.</div>}
              </>
        )}
      </div>
    </div>
  )
}
