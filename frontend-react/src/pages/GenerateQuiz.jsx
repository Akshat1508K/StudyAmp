import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { ClipboardList, Loader } from 'lucide-react';

const GenerateQuiz = () => {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState('');
  const [numMcq, setNumMcq] = useState(5);
  const [numShort, setNumShort] = useState(3);
  const [numLong, setNumLong] = useState(2);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

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
    try {
      const quiz = await api.generateQuiz(selectedDoc, numMcq, numShort, numLong);
      navigate('/quiz/take', { state: { quiz } });
    } catch (error) {
      console.error('Failed to generate quiz:', error);
    } finally {
      setLoading(false);
    }
  };

  const totalQuestions = numMcq + numShort + numLong;

  return (
    <div className="container">
      <h1 className="page-title">Generate Quiz</h1>
      <p className="page-subtitle">Create custom quizzes from your documents</p>

      <div className="grid grid-2">
        <div className="card">
          <h2 className="card-title"><ClipboardList size={20} />Configure Quiz</h2>
          <form onSubmit={handleGenerate}>
            <div className="form-group">
              <label className="label">Select Document</label>
              <select className="select" value={selectedDoc} onChange={(e) => setSelectedDoc(e.target.value)} required>
                <option value="">Choose a document</option>
                {documents.map((doc) => (
                  <option key={doc._id} value={doc._id}>{doc.file_name}</option>
                ))}
              </select>
            </div>
            <div className="grid grid-3">
              <div className="form-group">
                <label className="label">MCQs</label>
                <input type="number" className="input" min="0" max="20" value={numMcq} onChange={(e) => setNumMcq(Number(e.target.value))} />
              </div>
              <div className="form-group">
                <label className="label">Short Answer</label>
                <input type="number" className="input" min="0" max="10" value={numShort} onChange={(e) => setNumShort(Number(e.target.value))} />
              </div>
              <div className="form-group">
                <label className="label">Long Answer</label>
                <input type="number" className="input" min="0" max="5" value={numLong} onChange={(e) => setNumLong(Number(e.target.value))} />
              </div>
            </div>
            <div className="alert alert-info" style={{ marginBottom: '16px' }}>Total Questions: {totalQuestions}</div>
            <button type="submit" className="button button-primary" disabled={loading || totalQuestions === 0}>
              {loading ? <><Loader size={20} className="spinning" />Generating...</> : 'Generate Quiz'}
            </button>
          </form>
        </div>
        <div className="card">
          <h2 className="card-title">📋 Question Types</h2>
          <ul className="info-list">
            <li><strong>MCQs:</strong> Multiple choice with 4 options</li>
            <li><strong>Short Answer:</strong> Brief 2-3 sentence responses</li>
            <li><strong>Long Answer:</strong> Detailed paragraph explanations</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default GenerateQuiz;
