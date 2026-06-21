import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { MessageCircleQuestion, Send, Loader, BookOpen, Check, AlertCircle, Copy } from 'lucide-react';
import './AskQuestion.css';

const AskQuestion = () => {
  const [question, setQuestion] = useState('');
  const [selectedDoc, setSelectedDoc] = useState('');
  const [documents, setDocuments] = useState([]);
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const response = await api.getDocuments();
      setDocuments(response.documents || []);
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setAnswer(null);

    try {
      const result = await api.askQuestion(question, selectedDoc || undefined);
      console.log('API Response:', result);
      setAnswer(result);
    } catch (error) {
      console.error('Failed to get answer:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatAnswer = (text) => {
    if (!text) return null;

    // Split by double newlines for paragraphs
    const paragraphs = text.split('\n\n');
    
    return paragraphs.map((para, idx) => {
      para = para.trim();
      if (!para) return null;

      // Check if it's a heading (starts with ** or #)
      if (para.startsWith('**') && para.endsWith('**')) {
        const heading = para.replace(/\*\*/g, '');
        return <h3 key={idx} className="formatted-heading">{heading}</h3>;
      }

      // Check if it's a numbered section (Step 1:, 1., etc.)
      if (/^(Step \d+:|Formula \d+:|\d+\.|•)/i.test(para)) {
        return <div key={idx} className="formatted-section">{formatInlineText(para)}</div>;
      }

      // Check if it's a bullet point
      if (para.startsWith('*') || para.startsWith('-') || para.startsWith('•')) {
        return <li key={idx} className="formatted-list-item">{formatInlineText(para.substring(1))}</li>;
      }

      // Regular paragraph
      return <p key={idx} className="formatted-paragraph">{formatInlineText(para)}</p>;
    });
  };

  const formatInlineText = (text) => {
    // Format bold text (**text** or __text__)
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/__(.*?)__/g, '<strong>$1</strong>');
    
    // Format italic text (*text* or _text_)
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    text = text.replace(/_(.*?)_/g, '<em>$1</em>');
    
    // Format inline code (`code`)
    text = text.replace(/`(.*?)`/g, '<code>$1</code>');
    
    // Format formulas (anything with mathematical symbols)
    text = text.replace(/(𝑏\d+|[=+\-*/()]|\d+\.\d+|e\^\(-?\d+\.?\d*\))/g, '<span class="formula">$1</span>');

    return <span dangerouslySetInnerHTML={{ __html: text }} />;
  };

  const copyToClipboard = () => {
    if (answer?.answer) {
      navigator.clipboard.writeText(answer.answer);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.7) return '#10b981'; // Green
    if (confidence >= 0.4) return '#f59e0b'; // Orange
    return '#ef4444'; // Red
  };

  const getConfidenceLabel = (confidence) => {
    if (confidence >= 0.7) return 'High Confidence';
    if (confidence >= 0.4) return 'Medium Confidence';
    return 'Low Confidence';
  };

  return (
    <div className="ask-question-page">
      <div className="page-header">
        <h1 className="page-title">Ask a Question</h1>
        <p className="page-subtitle">Get answers from your uploaded documents</p>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h2 className="card-title">
            <MessageCircleQuestion size={20} />
            Your Question
          </h2>

          <form onSubmit={handleSubmit} className="question-form">
            <div className="form-group">
              <label className="label">Search in:</label>
              <select
                className="select"
                value={selectedDoc}
                onChange={(e) => setSelectedDoc(e.target.value)}
              >
                <option value="">All Documents</option>
                {documents.map((doc) => (
                  <option key={doc._id} value={doc._id}>
                    {doc.file_name} ({doc.subject_name})
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="label">Question:</label>
              <textarea
                className="textarea"
                rows={4}
                placeholder="e.g., Explain Logistic Regression from this doc. Also give top formulas in proper steps"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                required
              />
            </div>

            <button type="submit" className="button button-primary" disabled={loading}>
              {loading ? <Loader size={20} className="spinning" /> : <Send size={20} />}
              {loading ? 'Getting Answer...' : 'Get Answer'}
            </button>
          </form>
        </div>

        <div className="card">
          <h2 className="card-title">💡 Tips</h2>
          <ul className="tips-list">
            <li>Be specific and clear in your questions</li>
            <li>Use keywords from your uploaded documents</li>
            <li>Ask one concept at a time for better answers</li>
            <li>Try different phrasings if you don't get good results</li>
          </ul>

          {documents.length > 0 && (
            <>
              <h3 className="available-subjects-title">📚 Available Subjects</h3>
              <div className="subjects-list">
                {Array.from(new Set(documents.map(d => d.subject_name))).map((subject, idx) => (
                  <span key={idx} className="subject-badge">{subject}</span>
                ))}
              </div>
            </>
          )}
        </div>
      </div>

      {answer && (
        <div className="card answer-card">
          <div className="answer-header">
            <h2 className="answer-title">
              <span className="answer-icon">💡</span>
              Answer
            </h2>
            <div className="answer-actions">
              <div 
                className="confidence-badge" 
                style={{ 
                  background: `${getConfidenceColor(answer.confidence)}15`,
                  color: getConfidenceColor(answer.confidence),
                  border: `1px solid ${getConfidenceColor(answer.confidence)}40`
                }}
              >
                <Check size={16} />
                {getConfidenceLabel(answer.confidence)} ({(answer.confidence * 100).toFixed(0)}%)
              </div>
              <button 
                className="copy-button"
                onClick={copyToClipboard}
                title="Copy to clipboard"
              >
                {copied ? <Check size={18} /> : <Copy size={18} />}
                {copied ? 'Copied!' : 'Copy'}
              </button>
            </div>
          </div>

          <div className="answer-content">
            {formatAnswer(answer.answer)}
          </div>

          {answer.sources && answer.sources.length > 0 && (
            <div className="sources-section">
              <h3 className="sources-title">
                <BookOpen size={18} />
                Sources ({answer.sources.length})
              </h3>
              <div className="sources-grid">
                {answer.sources.slice(0, 5).map((source, idx) => (
                  <div key={idx} className="source-card">
                    <div className="source-header">
                      <span className="source-number">#{idx + 1}</span>
                      <span className="source-score">
                        Relevance: {(source.score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="source-subject">{source.subject}</div>
                    {source.page_numbers && source.page_numbers.length > 0 && (
                      <div className="source-pages">
                        Pages: {source.page_numbers.join(', ')}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {answer.confidence < 0.4 && (
            <div className="low-confidence-warning">
              <AlertCircle size={18} />
              <div>
                <strong>Low confidence answer</strong>
                <p>The answer might not be fully accurate. Try rephrasing your question or checking if the relevant document is uploaded.</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AskQuestion;
