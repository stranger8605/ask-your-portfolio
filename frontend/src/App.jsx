import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  PieChart, Pie, Cell 
} from 'recharts';
import { 
  TrendingUp, TrendingDown, PieChart as ChartIcon, 
  MessageSquare, Search, Info, ShieldCheck, ArrowRight
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = 'http://localhost:8000';

const App = () => {
  const [summary, setSummary] = useState(null);
  const [sectors, setSectors] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const summaryRes = await axios.get(`${API_BASE}/portfolio/summary`);
      const sectorsRes = await axios.get(`${API_BASE}/portfolio/sectors`);
      setSummary(summaryRes.data);
      setSectors(sectorsRes.data);
    } catch (err) {
      console.error("Error fetching data", err);
    }
  };

  const handleQuery = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/query`, { query });
      setAiResponse(res.data);
    } catch (err) {
      setAiResponse({
        answer: "I'm having trouble connecting to the intelligence engine. Please ensure the backend is running.",
        citations: [],
        confidence: 0
      });
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6'];

  return (
    <div className="dashboard-container">
      {/* Header Section */}
      <header style={{ marginBottom: '3rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '2rem', fontWeight: 700, letterSpacing: '-0.5px' }}>
            Ask<span style={{ color: 'var(--accent-primary)' }}>Your Portfolio</span>
          </h1>
          <p style={{ color: 'var(--text-secondary)' }}>Disciplined Financial Intelligence for HNI Clients</p>
        </div>
        <div className="premium-card" style={{ padding: '0.75rem 1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <ShieldCheck size={20} color="var(--accent-primary)" />
          <span style={{ fontSize: '0.875rem', fontWeight: 600 }}>Secure Terminal</span>
        </div>
      </header>

      {/* Stats Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="premium-card">
          <div className="stat-label">Total Portfolio Value</div>
          <div className="stat-value">₹{(summary?.total_current || 0).toLocaleString()}</div>
          <div style={{ color: 'var(--text-secondary)', marginTop: '0.5rem', fontSize: '0.9rem' }}>
            Invested: ₹{(summary?.total_invested || 0).toLocaleString()}
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="premium-card">
          <div className="stat-label">Day's Performance</div>
          <div className={`stat-value ${summary?.day_gain >= 0 ? 'success' : 'danger'}`} 
               style={{ color: summary?.day_gain >= 0 ? 'var(--success)' : 'var(--danger)' }}>
            {summary?.day_gain >= 0 ? '+' : ''}₹{(summary?.day_gain || 0).toLocaleString()}
          </div>
          <div style={{ color: 'var(--text-secondary)', marginTop: '0.5rem', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            {summary?.day_gain >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
            {summary?.day_return_pct}% Today
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="premium-card">
          <div className="stat-label">Total G/L</div>
          <div className="stat-value" style={{ color: 'var(--accent-primary)' }}>
            +{(summary?.total_return_pct || 0)}%
          </div>
          <div style={{ color: 'var(--text-secondary)', marginTop: '0.5rem', fontSize: '0.9rem' }}>
            Overall Profit: ₹{(summary?.total_gain || 0).toLocaleString()}
          </div>
        </motion.div>
      </div>

      {/* AI Intelligence Section */}
      <section className="query-container">
        <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <MessageSquare size={24} color="var(--accent-primary)" />
          Ask Portfolio Intelligence
        </h3>
        <form onSubmit={handleQuery} className="query-input-wrapper">
          <Search size={20} color="var(--text-secondary)" />
          <input 
            type="text" 
            className="query-input" 
            placeholder="Why is my portfolio down today? Or ask about sector risk..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button type="submit" className="query-button" disabled={loading}>
            {loading ? 'Analyzing...' : 'Ask AI'}
          </button>
        </form>

        <AnimatePresence>
          {aiResponse && (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="premium-card response-card"
            >
              <div style={{ fontSize: '1.1rem', lineHeight: '1.6', marginBottom: '1rem' }}>
                {aiResponse.answer}
              </div>
              <div className="citation-list">
                <span style={{ fontWeight: 700, color: 'var(--text-primary)', marginRight: '1rem' }}>SOURCES</span>
                {aiResponse.citations.map((cite, i) => (
                  <span key={i} className="tag">{cite}</span>
                ))}
                <span className="tag" style={{ marginLeft: 'auto', border: '1px solid var(--accent-primary)' }}>
                   Accuracy: {aiResponse.confidence * 100}%
                </span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </section>

      {/* Secondary Insights Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '2rem' }}>
        <div className="premium-card">
          <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ChartIcon size={20} color="var(--accent-secondary)" />
            Sector Concentration
          </h3>
          <div style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={sectors}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="current_value"
                  label={({ name, percentage }) => `${name} (${percentage.toFixed(1)}%)`}
                >
                  {sectors.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ background: 'var(--bg-secondary)', border: '1px solid var(--card-border)', borderRadius: '8px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="premium-card">
          <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <TrendingUp size={20} color="var(--accent-primary)" />
            Top Holdings
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {summary?.holdings?.slice(0, 4).map((stock, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', background: 'rgba(255,255,255,0.02)', borderRadius: '0.75rem' }}>
                <div>
                  <div style={{ fontWeight: 700 }}>{stock.ticker}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{stock.name}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontWeight: 600 }}>₹{stock.current_value.toLocaleString()}</div>
                  <div style={{ color: stock.return_pct >= 0 ? 'var(--success)' : 'var(--danger)', fontSize: '0.8rem' }}>
                    {stock.return_pct >= 0 ? '+' : ''}{stock.return_pct.toFixed(2)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
          <button style={{ marginTop: '1.5rem', width: '100%', background: 'transparent', border: '1px solid var(--card-border)', color: 'var(--text-secondary)', padding: '0.75rem', borderRadius: '0.75rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
            View All Holdings <ArrowRight size={16} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default App;
