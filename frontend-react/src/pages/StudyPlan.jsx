import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { GraduationCap, Loader, Calendar, TrendingDown, TrendingUp } from 'lucide-react';

const StudyPlan = () => {
  const [studyPlan, setStudyPlan] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadStudyPlan();
  }, []);

  const loadStudyPlan = async () => {
    setLoading(true);
    try {
      const plan = await api.getStudyPlan();
      setStudyPlan(plan);
    } catch (error) {
      console.error('Failed to load study plan:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const plan = await api.generateStudyPlan();
      setStudyPlan(plan);
    } catch (error) {
      console.error('Failed to generate study plan:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  if (!studyPlan) {
    return (
      <div className="container">
        <div className="card" style={{ textAlign: 'center', padding: '48px' }}>
          <GraduationCap size={64} style={{ margin: '0 auto 24px', color: 'var(--accent-blue)' }} />
          <h2>No Study Plan Yet</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>Take some quizzes first to generate a personalized study plan</p>
          <button onClick={handleGenerate} className="button button-primary">Generate Study Plan</button>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <h1 className="page-title">Study Plan</h1>
      <p className="page-subtitle">Your personalized learning roadmap</p>

      <div className="grid grid-2">
        <div className="card">
          <h2 className="card-title"><TrendingDown size={20} />Topics to Focus On</h2>
          {studyPlan.weak_topics?.map((topic, idx) => (
            <div key={idx} style={{ padding: '12px', background: 'var(--bg-tertiary)', borderRadius: '8px', marginBottom: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 600 }}>{topic.topic}</div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>{topic.attempts} attempts</div>
                </div>
                <div style={{ color: 'var(--accent-red)' }}>{(topic.accuracy * 100).toFixed(0)}%</div>
              </div>
            </div>
          ))}
        </div>

        <div className="card">
          <h2 className="card-title"><TrendingUp size={20} />Strong Topics</h2>
          {studyPlan.strong_topics?.map((topic, idx) => (
            <div key={idx} style={{ padding: '12px', background: 'var(--bg-tertiary)', borderRadius: '8px', marginBottom: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 600 }}>{topic.topic}</div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>{topic.attempts} attempts</div>
                </div>
                <div style={{ color: 'var(--accent-green)' }}>{(topic.accuracy * 100).toFixed(0)}%</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="card" style={{ marginTop: '24px' }}>
        <h2 className="card-title"><Calendar size={20} />Day-by-Day Plan</h2>
        <div className="grid grid-2">
          {studyPlan.study_plan?.map((day, idx) => (
            <div key={idx} style={{ padding: '16px', background: 'var(--bg-tertiary)', borderRadius: '8px', borderLeft: '4px solid var(--accent-blue)' }}>
              <div style={{ fontWeight: 700, color: 'var(--accent-blue)', marginBottom: '8px' }}>Day {day.day}</div>
              <div style={{ fontWeight: 600, marginBottom: '8px' }}>{day.topic}</div>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{day.description}</div>
            </div>
          ))}
        </div>
      </div>

      <button onClick={handleGenerate} className="button button-primary" style={{ marginTop: '24px' }}>
        <GraduationCap size={20} />Regenerate Study Plan
      </button>
    </div>
  );
};

export default StudyPlan;
