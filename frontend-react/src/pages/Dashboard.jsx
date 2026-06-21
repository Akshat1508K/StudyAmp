import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import {
  BookOpen,
  ClipboardCheck,
  TrendingUp,
  Award,
  Calendar,
  Activity,
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './Dashboard.css';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const dashboardData = await api.getDashboard();
      setData(dashboardData);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  const overview = data?.analytics_summary?.overview || {};
  const improvement = data?.analytics_summary?.improvement_rate || 0;

  return (
    <div className="dashboard">
      {/* Metrics Grid */}
      <div className="grid grid-4">
        <div className="metric-card">
          <div className="metric-icon blue">
            <BookOpen size={24} />
          </div>
          <div className="metric-content">
            <div className="metric-label">Total Documents</div>
            <div className="metric-value">{data?.total_documents || 0}</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon purple">
            <ClipboardCheck size={24} />
          </div>
          <div className="metric-content">
            <div className="metric-label">Quizzes Taken</div>
            <div className="metric-value">{overview.total_quizzes || 0}</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon green">
            <Award size={24} />
          </div>
          <div className="metric-content">
            <div className="metric-label">Average Score</div>
            <div className="metric-value">{overview.average_score?.toFixed(1) || 0}%</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon yellow">
            <TrendingUp size={24} />
          </div>
          <div className="metric-content">
            <div className="metric-label">Improvement</div>
            <div className="metric-value">
              {improvement > 0 ? '+' : ''}{improvement.toFixed(1)}%
            </div>
          </div>
        </div>
      </div>

      {/* Performance Chart */}
      {data?.analytics_summary?.performance_over_time?.length > 0 && (
        <div className="card chart-card">
          <h2 className="card-title">
            <Activity size={20} />
            Performance Over Time
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.analytics_summary.performance_over_time}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2d3139" />
              <XAxis dataKey="date" stroke="#6b7280" />
              <YAxis stroke="#6b7280" domain={[0, 100]} />
              <Tooltip
                contentStyle={{
                  background: '#1e2128',
                  border: '1px solid #2d3139',
                  borderRadius: '8px',
                }}
              />
              <Line
                type="monotone"
                dataKey="score"
                stroke="#3b82f6"
                strokeWidth={3}
                dot={{ fill: '#3b82f6', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Two Column Grid */}
      <div className="grid grid-2">
        {/* Recent Quizzes */}
        <div className="card">
          <h2 className="card-title">
            <ClipboardCheck size={20} />
            Recent Quizzes
          </h2>
          {data?.quiz_history && data.quiz_history.length > 0 ? (
            <div className="quiz-list">
              {data.quiz_history.slice(0, 5).map((quiz) => (
                <div key={quiz.id} className="quiz-item">
                  <div className="quiz-info">
                    <div className="quiz-id">Quiz #{quiz.id.substring(0, 8)}</div>
                    <div className="quiz-date">
                      <Calendar size={14} />
                      {new Date(quiz.date).toLocaleDateString()}
                    </div>
                  </div>
                  <div className={`quiz-score ${getScoreClass(quiz.score)}`}>
                    {quiz.score.toFixed(0)}%
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>No quizzes taken yet</p>
            </div>
          )}
        </div>

        {/* Topic Mastery */}
        <div className="card">
          <h2 className="card-title">
            <Award size={20} />
            Topic Mastery
          </h2>
          {data?.analytics_summary?.topic_mastery &&
          Object.keys(data.analytics_summary.topic_mastery).length > 0 ? (
            <div className="topic-list">
              {Object.entries(data.analytics_summary.topic_mastery)
                .slice(0, 5)
                .map(([topic, stats]) => (
                  <div key={topic} className="topic-item">
                    <div className="topic-info">
                      <div className="topic-name">{topic}</div>
                      <div className="topic-attempts">{stats.attempts} attempts</div>
                    </div>
                    <div className="topic-progress">
                      <div
                        className="topic-progress-bar"
                        style={{
                          width: `${stats.mastery}%`,
                          background: getMasteryColor(stats.mastery),
                        }}
                      ></div>
                    </div>
                    <div className="topic-score">{stats.mastery.toFixed(0)}%</div>
                  </div>
                ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>No topic data available</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const getScoreClass = (score) => {
  if (score >= 80) return 'excellent';
  if (score >= 60) return 'good';
  return 'needs-improvement';
};

const getMasteryColor = (mastery) => {
  if (mastery >= 80) return '#10b981';
  if (mastery >= 60) return '#f59e0b';
  return '#ef4444';
};

export default Dashboard;
