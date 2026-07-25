import { useEffect, useState } from 'react'
import {
  PieChart, Pie, Cell, Tooltip, BarChart, Bar, XAxis, YAxis,
  LineChart, Line, CartesianGrid, Legend, ReferenceLine, ResponsiveContainer
} from 'recharts'
import { getCategories, getSentiment, getTicketPriorities, getSentimentTrend } from '../api'
import { SENTIMENT_COLOR, URGENCY_COLOR } from '../constants'

const COLORS = ['#6366f1','#22c55e','#ef4444','#f97316','#eab308','#3b82f6','#a855f7','#14b8a6','#f43f5e','#84cc16','#fb923c','#0ea5e9']

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{background:'#0e1a2e',border:'1px solid #1e3050',borderRadius:8,padding:'10px 14px',fontSize:'0.8rem'}}>
      <p style={{color:'#94a3b8',marginBottom:4}}>{label}</p>
      {payload.map((p, i) => <p key={i} style={{color:p.color}}>{p.name}: <b>{p.value}</b></p>)}
    </div>
  )
}

export default function Analytics() {
  const [days, setDays] = useState(30)
  const [sender, setSender] = useState('')
  const [categories, setCategories] = useState([])
  const [sentiment, setSentiment] = useState([])
  const [tickets, setTickets] = useState([])
  const [trend, setTrend] = useState({ trend_data: [], deterioration_alerts: [] })

  useEffect(() => {
    getCategories().then(r => setCategories(r.data.filter(d => d.category))).catch(() => {})
    getSentiment().then(r => setSentiment(r.data.filter(d => d.sentiment))).catch(() => {})
    getTicketPriorities().then(r => setTickets(r.data)).catch(() => {})
  }, [])

  useEffect(() => {
    getSentimentTrend(days, sender).then(r => setTrend(r.data)).catch(() => {})
  }, [days, sender])

  const senders = [...new Set((trend.trend_data || []).map(d => d.sender))]

  return (
    <div>
      <div className="page-header">
        <h1>📊 Analytics Dashboard</h1>
        <p>Category distribution, sentiment trends, and ticket intelligence</p>
      </div>

      <div className="grid-2" style={{marginBottom:16}}>
        <div className="card">
          <h3>Email Categories</h3>
          {categories.length === 0
            ? <div className="empty" style={{padding:'32px 0'}}><div className="empty-icon">📊</div>No classified emails yet.</div>
            : <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie data={categories} dataKey="count" nameKey="category" cx="50%" cy="50%"
                    outerRadius={100} label={({ category, percent }) => `${category} ${(percent*100).toFixed(0)}%`}
                    labelLine={{ stroke: '#334155' }}>
                    {categories.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} stroke="transparent" />)}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>}
        </div>

        <div className="card">
          <h3>Sentiment Distribution</h3>
          {sentiment.length === 0
            ? <div className="empty" style={{padding:'32px 0'}}><div className="empty-icon">😐</div>No sentiment data yet.</div>
            : <ResponsiveContainer width="100%" height={280}>
                <BarChart data={sentiment} barSize={40}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e3050" />
                  <XAxis dataKey="sentiment" axisLine={false} tickLine={false} />
                  <YAxis axisLine={false} tickLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="count" radius={[6,6,0,0]}>
                    {sentiment.map((d, i) => <Cell key={i} fill={SENTIMENT_COLOR[d.sentiment] || '#6366f1'} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>}
        </div>
      </div>

      <div className="card" style={{marginBottom:16}}>
        <h3>Ticket Priority Distribution</h3>
        {tickets.length === 0
          ? <div className="empty" style={{padding:'24px 0'}}><div className="empty-icon">🎫</div>No tickets yet.</div>
          : <ResponsiveContainer width="100%" height={220}>
              <BarChart data={tickets} barSize={50}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e3050" />
                <XAxis dataKey="priority" axisLine={false} tickLine={false} />
                <YAxis axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" radius={[6,6,0,0]}>
                  {tickets.map((d, i) => <Cell key={i} fill={URGENCY_COLOR[d.priority] || '#6366f1'} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>}
      </div>

      <div className="card">
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:16,flexWrap:'wrap',gap:10}}>
          <h3>Sentiment Trend Over Time</h3>
          <div className="search-row" style={{margin:0}}>
            <label style={{fontSize:'0.825rem',color:'var(--text-muted)',display:'flex',alignItems:'center',gap:6}}>
              Days <input type="number" value={days} min={7} max={90} onChange={e => setDays(Number(e.target.value))} style={{width:64}} />
            </label>
            <input placeholder="Filter by sender" value={sender} onChange={e => setSender(e.target.value)} style={{minWidth:200}} />
          </div>
        </div>

        {(trend.trend_data || []).length === 0
          ? <div className="empty" style={{padding:'32px 0'}}><div className="empty-icon">📈</div>No trend data. Process emails first.</div>
          : <ResponsiveContainer width="100%" height={300}>
              <LineChart>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e3050" />
                <XAxis dataKey="timestamp" tickFormatter={v => v ? v.slice(0,10) : ''} axisLine={false} tickLine={false} />
                <YAxis axisLine={false} tickLine={false} domain={[-1, 1]} />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <ReferenceLine y={0} stroke="#475569" strokeDasharray="4 4" />
                <ReferenceLine y={-0.3} stroke="#ef4444" strokeDasharray="3 3" strokeOpacity={0.6} />
                {senders.map((s, i) => (
                  <Line key={s} type="monotone" dataKey="sentiment_score"
                    data={trend.trend_data.filter(d => d.sender === s)}
                    stroke={COLORS[i % COLORS.length]} name={s} dot={{ r: 3 }} strokeWidth={2} />
                ))}
              </LineChart>
            </ResponsiveContainer>}

        {(trend.deterioration_alerts || []).length > 0 && (
          <div style={{marginTop:16}}>
            <h4 style={{marginBottom:8}}>⚠️ Sentiment Deterioration Alerts</h4>
            {trend.deterioration_alerts.map((a, i) => (
              <div key={i} className="alert-box">🔴 <div><b>{a.sender}</b> — {a.alert}</div></div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
