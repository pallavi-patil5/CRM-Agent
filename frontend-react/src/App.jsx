import { BrowserRouter, NavLink, Routes, Route } from 'react-router-dom'
import MissionControl from './pages/MissionControl'
import ThreadWorkspace from './pages/ThreadWorkspace'
import Analytics from './pages/Analytics'
import RagDebug from './pages/RagDebug'
import BulkOperations from './pages/BulkOperations'
import './App.css'

const nav = [
  ['/', '🏠', 'Mission Control'],
  ['/threads', '📬', 'Thread Workspace'],
  ['/analytics', '📊', 'Analytics'],
  ['/rag', '🔍', 'RAG Debug'],
  ['/bulk', '⚙️', 'Bulk Operations'],
]

export default function App() {
  return (
    <BrowserRouter>
      <div className="layout">
        <aside className="sidebar">
          <div className="sidebar-brand">
            <div className="logo">🤖</div>
            <h2>Agentic CRM</h2>
            <span>v1.0 · llama3</span>
          </div>
          <nav>
            {nav.map(([path, icon, label]) => (
              <NavLink key={path} to={path} end={path === '/'} className={({ isActive }) => isActive ? 'active' : ''}>
                <span className="nav-icon">{icon}</span>{label}
              </NavLink>
            ))}
          </nav>
          <div className="sidebar-footer">
            <span className="status-dot" />API · localhost:8000
          </div>
        </aside>
        <main className="content">
          <Routes>
            <Route path="/" element={<MissionControl />} />
            <Route path="/threads" element={<ThreadWorkspace />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/rag" element={<RagDebug />} />
            <Route path="/bulk" element={<BulkOperations />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
