import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { CheckCircle, XCircle, Loader, ChevronLeft, ChevronRight } from 'lucide-react';

const TakeQuiz = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const quiz = location.state?.quiz;
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  if (!quiz) {
    return (
      <div className="container">
        <div className="alert alert-warning">No quiz found. Please generate a quiz first.</div>
        <button onClick={() => navigate('/quiz/generate')} className="button button-primary">Generate Quiz</button>
      </div>
    );
  }

  const totalQuestions = quiz.questions.length;
  const currentQ = quiz.questions[currentQuestion];

  const handleAnswerChange = (value) => {
    setAnswers({ ...answers, [currentQuestion]: value });
  };

  const handleNext = () => {
    if (currentQuestion < totalQuestions - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const result = await api.submitQuiz(quiz._id, answers);
      setResult(result);
    } catch (error) {
      console.error('Failed to submit quiz:', error);
      alert('Failed to submit quiz. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const getAnsweredCount = () => {
    return Object.keys(answers).length;
  };

  if (result) {
    return (
      <div className="container">
        <div className="card">
          <h1 style={{ marginBottom: '8px' }}>🎉 Quiz Results</h1>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>Here's how you did!</p>
          
          <div className="grid grid-4" style={{ marginBottom: '32px' }}>
            <div className="metric-card">
              <div className="metric-label">Score</div>
              <div className="metric-value" style={{ color: result.score >= 70 ? '#10b981' : result.score >= 50 ? '#f59e0b' : '#ef4444' }}>
                {result.score.toFixed(0)}%
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Correct</div>
              <div className="metric-value">{result.correct_answers}/{result.total_questions}</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Accuracy</div>
              <div className="metric-value">{(result.accuracy * 100).toFixed(0)}%</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Attempted</div>
              <div className="metric-value">{result.total_questions}</div>
            </div>
          </div>

          {result.strong_topics?.length > 0 && (
            <div style={{ marginBottom: '24px' }}>
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                <CheckCircle size={24} color="#10b981" />
                Strong Topics
              </h3>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {result.strong_topics.map((topic, idx) => (
                  <span key={idx} className="badge" style={{ background: 'rgba(16, 185, 129, 0.1)', color: '#10b981', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                    {topic}
                  </span>
                ))}
              </div>
            </div>
          )}

          {result.weak_topics?.length > 0 && (
            <div style={{ marginBottom: '24px' }}>
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                <XCircle size={24} color="#f59e0b" />
                Topics to Review
              </h3>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {result.weak_topics.map((topic, idx) => (
                  <span key={idx} className="badge badge-warning">{topic}</span>
                ))}
              </div>
            </div>
          )}

          {/* Detailed Results Section */}
          <div style={{ marginTop: '32px', paddingTop: '32px', borderTop: '1px solid var(--border-color)' }}>
            <h2 style={{ marginBottom: '24px' }}>📝 Question-by-Question Review</h2>
            
            {result.detailed_results?.map((detail, idx) => (
              <div 
                key={idx} 
                style={{ 
                  marginBottom: '24px', 
                  padding: '20px',
                  background: detail.is_correct ? 'rgba(16, 185, 129, 0.05)' : 'rgba(239, 68, 68, 0.05)',
                  border: `2px solid ${detail.is_correct ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                  borderRadius: '12px'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                  {detail.is_correct ? (
                    <CheckCircle size={24} color="#10b981" />
                  ) : (
                    <XCircle size={24} color="#ef4444" />
                  )}
                  <span className="badge" style={{ background: 'rgba(59, 130, 246, 0.1)', color: '#3b82f6' }}>
                    {detail.topic}
                  </span>
                  <span className="badge" style={{ background: 'rgba(139, 92, 246, 0.1)', color: '#8b5cf6' }}>
                    {detail.question_type === 'mcq' ? 'MCQ' : 
                     detail.question_type === 'short_answer' ? 'Short Answer' : 
                     'Long Answer'}
                  </span>
                </div>

                <h4 style={{ marginBottom: '16px', fontSize: '16px', lineHeight: '1.6' }}>
                  Q{idx + 1}. {detail.question}
                </h4>

                <div style={{ marginBottom: '12px' }}>
                  <strong style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>Your Answer:</strong>
                  <div style={{ 
                    marginTop: '8px', 
                    padding: '12px', 
                    background: 'var(--bg-tertiary)', 
                    borderRadius: '8px',
                    color: detail.is_correct ? '#10b981' : '#ef4444',
                    fontWeight: '500'
                  }}>
                    {detail.user_answer || '[No answer provided]'}
                  </div>
                </div>

                {!detail.is_correct && (
                  <div>
                    <strong style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>Correct Answer:</strong>
                    <div style={{ 
                      marginTop: '8px', 
                      padding: '12px', 
                      background: 'rgba(16, 185, 129, 0.1)', 
                      borderRadius: '8px',
                      color: '#10b981',
                      fontWeight: '500',
                      border: '1px solid rgba(16, 185, 129, 0.3)'
                    }}>
                      {detail.correct_answer}
                    </div>
                  </div>
                )}

                {detail.is_correct && detail.question_type !== 'mcq' && (
                  <div style={{ marginTop: '12px', fontSize: '14px', color: '#10b981' }}>
                    ✓ Your answer correctly covered the key concepts!
                  </div>
                )}
              </div>
            ))}
          </div>

          <div style={{ display: 'flex', gap: '12px', marginTop: '32px' }}>
            <button onClick={() => navigate('/dashboard')} className="button button-primary">
              Back to Dashboard
            </button>
            <button onClick={() => navigate('/quiz/generate')} className="button button-secondary">
              Generate New Quiz
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div style={{ marginBottom: '24px' }}>
        <h1 className="page-title">Take Quiz</h1>
        <p className="page-subtitle">Answer all questions and submit</p>
      </div>

      {/* Progress Bar */}
      <div className="card" style={{ marginBottom: '16px', padding: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <span style={{ fontSize: '14px', fontWeight: '500' }}>
            Question {currentQuestion + 1} of {totalQuestions}
          </span>
          <span style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
            Answered: {getAnsweredCount()}/{totalQuestions}
          </span>
        </div>
        <div style={{ height: '8px', background: 'var(--bg-secondary)', borderRadius: '4px', overflow: 'hidden' }}>
          <div 
            style={{ 
              height: '100%', 
              background: 'linear-gradient(90deg, #3b82f6, #8b5cf6)', 
              width: `${((currentQuestion + 1) / totalQuestions) * 100}%`,
              transition: 'width 0.3s ease'
            }}
          />
        </div>
      </div>

      {/* Question Card */}
      <div className="card">
        <div style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <span className="badge" style={{ background: 'rgba(59, 130, 246, 0.1)', color: '#3b82f6' }}>
              {currentQ.topic || 'General'}
            </span>
            <span className="badge" style={{ background: 'rgba(139, 92, 246, 0.1)', color: '#8b5cf6' }}>
              {currentQ.question_type === 'mcq' ? 'Multiple Choice' : 
               currentQ.question_type === 'short_answer' ? 'Short Answer' : 
               'Long Answer'}
            </span>
            {answers[currentQuestion] && (
              <span className="badge" style={{ background: 'rgba(16, 185, 129, 0.1)', color: '#10b981' }}>
                ✓ Answered
              </span>
            )}
          </div>
          <h2 style={{ fontSize: '20px', lineHeight: '1.6', marginBottom: '24px' }}>
            {currentQ.question}
          </h2>
        </div>

        {/* Answer Input */}
        {currentQ.question_type === 'mcq' ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {currentQ.options?.map((opt, optIdx) => {
              const optionLetter = opt.charAt(0); // Extract A, B, C, D from "A) option text"
              const isSelected = answers[currentQuestion] === optionLetter;
              
              return (
                <label 
                  key={optIdx} 
                  style={{ 
                    display: 'flex', 
                    alignItems: 'flex-start', 
                    gap: '12px', 
                    padding: '16px',
                    border: isSelected ? '2px solid #3b82f6' : '2px solid var(--border-color)',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    background: isSelected ? 'rgba(59, 130, 246, 0.05)' : 'transparent',
                    transition: 'all 0.2s ease'
                  }}
                  className="option-hover"
                >
                  <input 
                    type="radio" 
                    name={`q${currentQuestion}`} 
                    value={optionLetter}
                    checked={isSelected}
                    onChange={(e) => handleAnswerChange(e.target.value)}
                    style={{ marginTop: '2px' }}
                  />
                  <span style={{ flex: 1, lineHeight: '1.6' }}>{opt}</span>
                </label>
              );
            })}
          </div>
        ) : (
          <div>
            <textarea 
              className="textarea" 
              rows={currentQ.question_type === 'long_answer' ? 8 : 4}
              placeholder={
                currentQ.question_type === 'short_answer' 
                  ? 'Enter your answer (2-4 sentences)' 
                  : 'Enter your detailed answer (1-2 paragraphs)'
              }
              value={answers[currentQuestion] || ''} 
              onChange={(e) => handleAnswerChange(e.target.value)}
              style={{ width: '100%', fontSize: '15px', lineHeight: '1.6' }}
            />
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '8px' }}>
              {currentQ.question_type === 'short_answer' 
                ? '💡 Write a concise answer covering the main points' 
                : '💡 Provide a comprehensive explanation with details and examples'}
            </p>
          </div>
        )}

        {/* Navigation Buttons */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '32px', paddingTop: '24px', borderTop: '1px solid var(--border-color)' }}>
          <button 
            onClick={handlePrevious} 
            className="button button-secondary"
            disabled={currentQuestion === 0}
            style={{ opacity: currentQuestion === 0 ? 0.5 : 1 }}
          >
            <ChevronLeft size={20} />
            Previous
          </button>

          {currentQuestion === totalQuestions - 1 ? (
            <button 
              onClick={handleSubmit} 
              className="button button-primary"
              disabled={submitting || getAnsweredCount() === 0}
            >
              {submitting ? (
                <>
                  <Loader size={20} className="spinning" />
                  Submitting...
                </>
              ) : (
                <>
                  Submit Quiz
                  <CheckCircle size={20} />
                </>
              )}
            </button>
          ) : (
            <button 
              onClick={handleNext} 
              className="button button-primary"
            >
              Next
              <ChevronRight size={20} />
            </button>
          )}
        </div>

        {/* Question Navigation Dots */}
        <div style={{ display: 'flex', gap: '8px', justifyContent: 'center', marginTop: '24px', flexWrap: 'wrap' }}>
          {quiz.questions.map((_, idx) => (
            <button
              key={idx}
              onClick={() => setCurrentQuestion(idx)}
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                border: currentQuestion === idx ? '2px solid #3b82f6' : '2px solid var(--border-color)',
                background: answers[idx] ? '#3b82f6' : currentQuestion === idx ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                color: answers[idx] ? '#fff' : 'var(--text-primary)',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: '500',
                transition: 'all 0.2s ease'
              }}
              title={`Question ${idx + 1}${answers[idx] ? ' (Answered)' : ''}`}
            >
              {idx + 1}
            </button>
          ))}
        </div>
      </div>

      {/* Warning if not all answered */}
      {currentQuestion === totalQuestions - 1 && getAnsweredCount() < totalQuestions && (
        <div className="alert alert-warning" style={{ marginTop: '16px' }}>
          ⚠️ You have answered {getAnsweredCount()} out of {totalQuestions} questions. 
          Unanswered questions will be marked as incorrect.
        </div>
      )}
    </div>
  );
};

export default TakeQuiz;
