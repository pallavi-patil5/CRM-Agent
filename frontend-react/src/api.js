import axios from 'axios'

const api = axios.create({ baseURL: 'http://localhost:8000' })

export const getSummary = () => api.get('/dashboard/summary')
export const getEmails = () => api.get('/dashboard/emails')
export const getCategories = () => api.get('/dashboard/categories')
export const getSentiment = () => api.get('/dashboard/sentiment')
export const getTicketPriorities = () => api.get('/dashboard/tickets')
export const getTickets = () => api.get('/tickets')
export const processEmail = (id) => api.post(`/process-email/${id}`)
export const dryRunEmail = (id) => api.post(`/agent/dry-run/${id}`)
export const processAll = () => api.post('/process-all-emails')
export const getContact = (email) => api.get(`/contacts/${email}`)
export const getThreads = (email) => api.get(`/threads/contact/${email}`)
export const ragSearch = (q, top_k = 5) => api.get(`/rag/search?q=${encodeURIComponent(q)}&top_k=${top_k}`)
export const getSentimentTrend = (days, sender) =>
  api.get(`/analytics/sentiment-trend?days=${days}${sender ? `&sender=${sender}` : ''}`)
export const gmailStatus = () => api.get('/gmail/status')
export const gmailSync = (maxResults, markRead) => api.post(`/gmail/sync?max_results=${maxResults}&mark_read=${markRead}`)
