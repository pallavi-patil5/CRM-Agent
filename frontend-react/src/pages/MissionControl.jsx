import { useEffect, useState } from 'react'
import { getSummary, getEmails, getTickets, processEmail, dryRunEmail } from '../api'
import { CATEGORY_ICON, URGENCY_ICON, SENTIMENT_ICON } from '../constants'

const urgencyClass = u => ({ Critical: 'urgency-critical', High: 'urgency-high', Medium: 'urgency-medium', Low: 'urgency-low' }[u] || '')
const badgeClass = u => ({ Critical: 'badge-critical', High: 'badge-high', Medium: 'badge-medium', Low: 'badge-low' }[u] || 'badge-neutral')
const sentimentBadge = s => ({ Positive: 'badge-positive', Negative: 'badge-negative', Neutral: 'badge-neutral', Mixed: 'badge-mixed' }[s] || 'badge-neutral')

function EmailCard({ email }) {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [mode, setMode] = useState(null)

  const handle = async (fn, m) => {
    setLoading(true); setMode(m); setResult(null)
    try { const r = await fn(email.id); setResult(r.data) }
    catch (e) { setResult({ error: String(e) }) }
    finally { setLoading(false) }
  }

  return (
    <details className={`card ${urgencyClass(email.urgency)}`}>
      <summary>
        <span className="email-id">#{email.id}</span>
        <span className="email-subject">{email.subject || '(no subject)'}</span>
        <div className="email-meta">
          {email.urgency && <span className={`badge ${badgeClass(email.urgency)}`}>{URGENCY_ICON[email.urgency]} {email.urgency}</span>}
          {email.sentiment && <span className={`badge ${sentimentBadge(email.sentiment)}`}>{SENTIMENT_ICON[email.sentiment]} {email.sentiment}</span>}
          {email.category && <span className="badge badge-category">{CATEGORY_ICON[email.category] || '📧'} {email.category}</span>}
        </div>
      </summary>
      <div className="card-body">
        <p><span style={{color:'var(--text-muted)'}}>From:</span> {email.sender}</p>
        <p style={{color:'var(--text-soft)',lineHeight:'1.6'}}>{String(email.body || '').slice(0, 300)}…</p>
        {email.confidence && <p><span style={{color:'var(--text-muted)'}}>Confidence:</span> {(email.confidence * 100).toFixed(0)}%</p>}
        <div className="btn-row">
          <button onClick={() => handle(processEmail, 'live')} disabled={loading}>
            {loading && mode === 'live' ? <><span className="spinner" /> Running…</> : '🤖 Process'}
          </button>
          <button className="btn-secondary" onClick={() => handle(dryRunEmail, 'dry')} disabled={loading}>
            {loading && mode === 'dry' ? <><span className="spinner" /> Planning…</> : '🔍 Dry Run'}
          </button>
        </div>
        {result && (
          result.error
            ? <div className="alert-box">⚠️ {result.error}</div>
            : <>
              {result.draft_reply && <><h4 style={{marginTop:8}}>📝 Draft Reply</h4><textarea readOnly value={result.draft_reply} rows={4} style={{width:'100%'}} /></>}
              {result.reasoning_trace?.length > 0 && result.reasoning_trace.map((s, i) => (
                <div key={i} className="trace-step">
                  <div className="trace-header"><span className="trace-step-badge">Step {s.step}</span>{s.action}</div>
                  <p>💭 {s.thought}</p>
                  {s.observation && <p>👁 {s.observation}</p>}
                </div>
              ))}
              {mode === 'dry' && <pre className="json-box">{JSON.stringify(result.classification, null, 2)}</pre>}
            </>
        )}
      </div>
    </details>
  )
}

export default function MissionControl() {
  const [summary, setSummary] = useState({})
  const [emails, setEmails] = useState([])
  const [tickets, setTickets] = useState([])
  const [tab, setTab] = useState('all')

  useEffect(() => {
    getSummary().then(r => setSummary(r.data)).catch(() => {})
    getEmails().then(r => setEmails(r.data)).catch(() => {})
    getTickets().then(r => setTickets(r.data)).catch(() => {})
  }, [])

  const filtered = {
    all: emails,
    human: emails.filter(e => e.requires_human),
    escalated: emails.filter(e => ['Critical', 'High'].includes(e.urgency)),
    spam: emails.filter(e => e.category === 'Spam'),
  }

  const priorityBadge = p => <span className={`badge ${badgeClass(p)}`}>{p}</span>
  const statusBadge = s => <span className={`badge ${s === 'Open' ? 'badge-high' : 'badge-positive'}`}>{s}</span>

  return (
    <div>
      <div className="page-header">
        <h1>📧 Mission Control</h1>
        <p>Real-time email inbox with AI triage and autonomous agent processing</p>
      </div>

      <div className="metrics-row">
        <div className="metric"><span className="metric-icon">📨</span><div className="metric-value">{summary.total_emails ?? 0}</div><div className="metric-label">Total Emails</div></div>
        <div className="metric"><span className="metric-icon">🎫</span><div className="metric-value">{summary.total_tickets ?? 0}</div><div className="metric-label">Total Tickets</div></div>
        <div className="metric"><span className="metric-icon">🔓</span><div className="metric-value">{summary.open_tickets ?? 0}</div><div className="metric-label">Open Tickets</div></div>
        <div className="metric"><span className="metric-icon">✅</span><div className="metric-value">{summary.closed_tickets ?? 0}</div><div className="metric-label">Closed Tickets</div></div>
      </div>

      <div className="tabs">
        {[['all','All Emails'],['human','Needs Human'],['escalated','Escalated'],['spam','Spam']].map(([k, l]) => (
          <button key={k} className={tab === k ? 'active' : ''} onClick={() => setTab(k)}>
            {l}<span className="tab-count">{filtered[k].length}</span>
          </button>
        ))}
      </div>

      <div className="email-list">
        {filtered[tab].length === 0
          ? <div className="empty"><div className="empty-icon">📭</div>No emails in this category.</div>
          : filtered[tab].map(e => <EmailCard key={e.id} email={e} />)}
      </div>

      <div className="section">
        <div className="section-header"><h2>🎫 Tickets</h2></div>
        {tickets.length === 0
          ? <div className="empty"><div className="empty-icon">🎫</div>No tickets yet. Process emails to generate tickets.</div>
          : <div className="table-wrap">
              <table>
                <thead><tr><th>ID</th><th>Title</th><th>Priority</th><th>Status</th><th>Assignee</th></tr></thead>
                <tbody>{tickets.map(t => (
                  <tr key={t.id}>
                    <td style={{color:'var(--text-muted)',fontFamily:'monospace'}}>#{t.id}</td>
                    <td>{t.title}</td>
                    <td>{priorityBadge(t.priority)}</td>
                    <td>{statusBadge(t.status)}</td>
                    <td style={{color:'var(--text-soft)'}}>{t.assignee || '—'}</td>
                  </tr>
                ))}</tbody>
              </table>
            </div>}
      </div>
    </div>
  )
}
