import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { BarChart3, TrendingUp, Target, AlertTriangle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Analytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const data = await api.getAnalytics();
      setAnalytics(data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  if (!analytics || !analytics.overview) {
    return (
      <div className="container">
        <div className="alert alert-info">No analytics data available. Take some quizzes to see your performance!</div>
      </div>
    );
  }

  const topicMasteryData = Object.entries(analytics.topic_mastery || {}).map(([topic, data]) => ({
    topic,
    mastery: data.mastery,
  }));

  return (
    <div className="container">
      <h1 className="page-title">Learning Analytics</h1>
      <p className="page-subtitle">Track your progress and performance</p>

      <div className="grid grid-4">
        <div className="metric-card">
          <div className="metric-icon blue"><BarChart3 size={24} /></div>
          <div className="metric-content">
            <div className="metric-label">Total Quizzes</div>
            <div className="metric-value">{analytics.overview.total_quizzes}</div>
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon green"><Target size={24} /></div>
          <div className="metric-content">
            <div className="metric-label">Average Score</div>
            <div className="metric-value">{analytics.overview.average_score.toFixed(1)}%</div>
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon purple"><TrendingUp size={24} /></div>
          <div className="metric-content">
            <div className="metric-label">Total Questions</div>
            <div className="metric-value">{analytics.overview.total_questions}</div>
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon yellow"><TrendingUp size={24} /></div>
          <div className="metric-content">
            <div className="metric-label">Improvement</div>
            <div className="metric-value">{analytics.improvement_rate > 0 ? '+' : ''}{analytics.improvement_rate.toFixed(1)}%</div>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: '24px' }}>
        <h2 className="card-title"><Target size={20} />Topic Mastery</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={topicMasteryData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2d3139" />
            <XAxis dataKey="topic" stroke="#6b7280" />
            <YAxis stroke="#6b7280" domain={[0, 100]} />
            <Tooltip contentStyle={{ background: '#1e2128', border: '1px solid #2d3139', borderRadius: '8px' }} />
            <Bar dataKey="mastery" fill="#3b82f6" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {analytics.frequently_incorrect_topics?.length > 0 && (
        <div className="card" style={{ marginTop: '24px' }}>
          <h2 className="card-title"><AlertTriangle size={20} />Topics Needing Attention</h2>
          {analytics.frequently_incorrect_topics.map((item, idx) => (
            <div key={idx} style={{ padding: '12px', background: 'var(--bg-tertiary)', borderRadius: '8px', marginBottom: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontWeight: 600 }}>{item.topic}</span>
              <span className="badge badge-error">❌ {item.count} incorrect</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Analytics;
