import { useState } from 'react'
import { getContact, getThreads, processEmail, dryRunEmail } from '../api'
import { SENTIMENT_ICON, URGENCY_ICON, CATEGORY_ICON } from '../constants'

const sentimentBadge = s => ({ Positive: 'badge-positive', Negative: 'badge-negative', Neutral: 'badge-neutral', Mixed: 'badge-mixed' }[s] || 'badge-neutral')
const urgencyBadge = u => ({ Critical: 'badge-critical', High: 'badge-high', Medium: 'badge-medium', Low: 'badge-low' }[u] || 'badge-neutral')
const urgencyClass = u => ({ Critical: 'urgency-critical', High: 'urgency-high', Medium: 'urgency-medium', Low: 'urgency-low' }[u] || '')

export default function ThreadWorkspace() {
  const [emailInput, setEmailInput] = useState('')
  const [contact, setContact] = useState(null)
  const [threads, setThreads] = useState([])
  const [results, setResults] = useState({})
  const [loading, setLoading] = useState({})
  const [searched, setSearched] = useState(false)

  const load = async () => {
    if (!emailInput) return
    setSearched(true)
    try {
      const [c, t] = await Promise.all([getContact(emailInput), getThreads(emailInput)])
      setContact(c.data)
      setThreads(t.data)
    } catch { setContact(null); setThreads([]) }
  }

  const handle = async (fn, id) => {
    setLoading(l => ({ ...l, [id]: true }))
    try { const r = await fn(id); setResults(p => ({ ...p, [id]: r.data })) }
    catch (e) { setResults(p => ({ ...p, [id]: { error: String(e) } })) }
    finally { setLoading(l => ({ ...l, [id]: false })) }
  }

  const churnColor = score => score > 0.7 ? '#ef4444' : score > 0.4 ? '#f97316' : '#22c55e'

  return (
    <div>
      <div className="page-header">
        <h1>📬 Thread Workspace</h1>
        <p>View full conversation history and contact intelligence for any sender</p>
      </div>

      <div className="search-row">
        <input className="input-wide" value={emailInput} onChange={e => setEmailInput(e.target.value)}
          placeholder="Enter sender email e.g. bob.jones@enterprise.net"
          onKeyDown={e => e.key === 'Enter' && load()} />
        <button onClick={load}>🔎 Load Contact</button>
      </div>

      {searched && contact && (
        <div className="two-col">
          <div>
            {threads.length === 0
              ? <div className="empty"><div className="empty-icon">🧵</div>No threads found for this contact.</div>
              : threads.map(thread => (
                <div key={thread.thread_id} className="card" style={{marginBottom:16}}>
                  <div style={{display:'flex',alignItems:'center',gap:10,marginBottom:12}}>
                    <span style={{fontSize:'1rem'}}>🧵</span>
                    <div>
                      <div style={{fontWeight:600,fontSize:'0.9rem'}}>{thread.thread_id}</div>
                      <div style={{color:'var(--text-muted)',fontSize:'0.8rem'}}>{thread.subject}</div>
                    </div>
                    <span className={`badge ${thread.status === 'Open' ? 'badge-high' : 'badge-positive'}`} style={{marginLeft:'auto'}}>{thread.status}</span>
                  </div>
                  <div style={{display:'flex',flexDirection:'column',gap:6}}>
                    {thread.emails.map(e => (
                      <details key={e.id} className={`card ${urgencyClass(e.urgency)}`}>
                        <summary>
                          <span style={{color:'var(--text-muted)',fontFamily:'monospace',fontSize:'0.78rem'}}>#{e.id}</span>
                          <span style={{flex:1,fontWeight:500,fontSize:'0.875rem'}}>{e.subject}</span>
                          <div className="email-meta">
                            {e.urgency && <span className={`badge ${urgencyBadge(e.urgency)}`}>{URGENCY_ICON[e.urgency]} {e.urgency}</span>}
                            {e.sentiment && <span className={`badge ${sentimentBadge(e.sentiment)}`}>{SENTIMENT_ICON[e.sentiment]} {e.sentiment}</span>}
                            {e.category && <span className="badge badge-category">{CATEGORY_ICON[e.category] || '📧'} {e.category}</span>}
                          </div>
                        </summary>
                        <div className="card-body">
                          <div className="btn-row">
                            <button onClick={() => handle(processEmail, e.id)} disabled={loading[e.id]}>
                              {loading[e.id] ? <><span className="spinner" /> Running…</> : '🤖 Process'}
                            </button>
                            <button className="btn-secondary" onClick={() => handle(dryRunEmail, e.id)} disabled={loading[e.id]}>🔍 Dry Run</button>
                          </div>
                          {results[e.id] && (
                            results[e.id].error
                              ? <div className="alert-box">{results[e.id].error}</div>
                              : <>
                                {results[e.id].reasoning_trace?.map((s, i) => (
                                  <div key={i} className="trace-step">
                                    <div className="trace-header"><span className="trace-step-badge">Step {s.step}</span>{s.action}</div>
                                    <p>💭 {s.thought}</p>
                                    {s.observation && <p>👁 {s.observation}</p>}
                                  </div>
                                ))}
                                {results[e.id].draft_reply && (
                                  <><h4>📝 Draft Reply</h4>
                                  <textarea readOnly value={results[e.id].draft_reply} rows={4} style={{width:'100%'}} /></>
                                )}
                                {results[e.id].rag_policy_sources && (
                                  <div className="info-box">📚 Sources: {results[e.id].rag_policy_sources}</div>
                                )}
                              </>
                          )}
                        </div>
                      </details>
                    ))}
                  </div>
                </div>
              ))}
          </div>

          <div>
            <div className="card">
              <h3 style={{marginBottom:16}}>👤 Contact Profile</h3>
              {contact.error
                ? <div className="info-box">Contact not found in CRM.</div>
                : <div className="contact-card">
                    <div className="contact-row"><span className="label">Email</span><span className="value" style={{fontSize:'0.83rem'}}>{contact.email}</span></div>
                    <div className="contact-row"><span className="label">Name</span><span className="value">{contact.name || '—'}</span></div>
                    <div className="contact-row"><span className="label">Company</span><span className="value">{contact.company || '—'}</span></div>
                    <div className="contact-row">
                      <span className="label">Status</span>
                      <span className={`badge ${contact.status === 'Active' ? 'badge-positive' : contact.status === 'Churned' ? 'badge-critical' : 'badge-neutral'}`}>{contact.status}</span>
                    </div>
                    <div className="contact-row"><span className="label">Account Value</span><span className="value" style={{color:'#86efac'}}>${Number(contact.account_value||0).toLocaleString()}</span></div>
                    <div className="contact-row">
                      <span className="label">Churn Risk</span>
                      <span className="value" style={{color: churnColor(contact.churn_risk_score)}}>{(contact.churn_risk_score * 100).toFixed(0)}%</span>
                    </div>
                    <div className="contact-row"><span className="label">Avg Sentiment</span><span className="value">{contact.avg_sentiment_score ?? '—'}</span></div>
                    <div className="contact-row"><span className="label">Open Tickets</span><span className="value">{contact.open_tickets}</span></div>
                    <div className="contact-row"><span className="label">Threads</span><span className="value">{contact.thread_count}</span></div>
                  </div>}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
