import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { FileText, Loader } from 'lucide-react';

const GenerateSummary = () => {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState('');
  const [summaryType, setSummaryType] = useState('short');
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);

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

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!selectedDoc) return;

    setLoading(true);
    setSummary(null);

    try {
      const result = await api.generateSummary(selectedDoc, summaryType);
      setSummary(result);
    } catch (error) {
      console.error('Failed to generate summary:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1 className="page-title">Generate Summary</h1>
      <p className="page-subtitle">Create summaries of your study material</p>

      <div className="grid grid-2">
        <div className="card">
          <h2 className="card-title"><FileText size={20} />Generate</h2>
          <form onSubmit={handleGenerate}>
            <div className="form-group">
              <label className="label">Select Document</label>
              <select className="select" value={selectedDoc} onChange={(e) => setSelectedDoc(e.target.value)} required>
                <option value="">Choose a document</option>
                {documents.map((doc) => (
                  <option key={doc._id} value={doc._id}>{doc.file_name} ({doc.subject_name})</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="label">Summary Type</label>
              <select className="select" value={summaryType} onChange={(e) => setSummaryType(e.target.value)}>
                <option value="short">Short Summary</option>
                <option value="detailed">Detailed Summary</option>
                <option value="exam_day">Exam Day Summary</option>
              </select>
            </div>
            <button type="submit" className="button button-primary" disabled={loading}>
              {loading ? <><Loader size={20} className="spinning" />Generating...</> : 'Generate Summary'}
            </button>
          </form>
          {summary && (
            <div style={{ marginTop: '24px', padding: '16px', background: 'var(--bg-tertiary)', borderRadius: '8px' }}>
              <h3>Summary</h3>
              <p style={{ lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>{summary.content}</p>
            </div>
          )}
        </div>
        <div className="card">
          <h2 className="card-title">📋 Summary Types</h2>
          <ul className="info-list">
            <li><strong>Short:</strong> Quick 3-5 bullet point overview</li>
            <li><strong>Detailed:</strong> Comprehensive summary with all major topics</li>
            <li><strong>Exam Day:</strong> Key formulas, definitions, and exam focus points</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default GenerateSummary;
