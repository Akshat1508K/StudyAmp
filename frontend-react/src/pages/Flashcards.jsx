import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { BookMarked, Loader, ChevronLeft, ChevronRight, RotateCcw, Sparkles } from 'lucide-react';

const Flashcards = () => {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState('');
  const [numCards, setNumCards] = useState(5);
  const [flashcards, setFlashcards] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
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
    setFlashcards([]);
    setCurrentIndex(0);

    try {
      const result = await api.generateFlashcards(selectedDoc, numCards);
      setFlashcards(result.flashcards || []);
    } catch (error) {
      console.error('Failed to generate flashcards:', error);
      alert('Failed to generate flashcards. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (currentIndex < flashcards.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const handleReset = () => {
    setCurrentIndex(0);
  };

  const renderFlashcard = (card) => {
    if (!card) return null;

    switch (card.type) {
      case 'key_point':
        return (
          <div className="flashcard-content key-point-card">
            <div className="card-type-badge">📌 Key Points</div>
            <h2 className="flashcard-topic">{card.topic}</h2>
            <div className="key-points-list">
              {card.points.map((point, idx) => (
                <div key={idx} className="key-point-item">
                  <span className="point-number">{idx + 1}</span>
                  <span className="point-text">{point}</span>
                </div>
              ))}
            </div>
          </div>
        );

      case 'concept':
        return (
          <div className="flashcard-content concept-card">
            <div className="card-type-badge">💡 Concept</div>
            <h2 className="flashcard-question">{card.question}</h2>
            <div className="concept-answer">
              <p>{card.answer}</p>
            </div>
          </div>
        );

      case 'comparison':
        return (
          <div className="flashcard-content comparison-card">
            <div className="card-type-badge">⚖️ Comparison</div>
            <h2 className="flashcard-topic">{card.topic}</h2>
            <div className="comparison-grid">
              <div className="comparison-side left-side">
                <h3>{card.topic.split(' vs ')[0]}</h3>
                <ul>
                  {card.left_points.map((point, idx) => (
                    <li key={idx}>{point}</li>
                  ))}
                </ul>
              </div>
              <div className="vs-divider">VS</div>
              <div className="comparison-side right-side">
                <h3>{card.topic.split(' vs ')[1] || 'Other'}</h3>
                <ul>
                  {card.right_points.map((point, idx) => (
                    <li key={idx}>{point}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        );

      default:
        return <div>Unknown card type</div>;
    }
  };

  return (
    <div className="container">
      <h1 className="page-title">📚 Flashcards</h1>
      <p className="page-subtitle">Quick revision with key points, concepts, and comparisons</p>

      {!flashcards.length ? (
        <div className="grid grid-2">
          <div className="card">
            <h2 className="card-title">
              <BookMarked size={20} />
              Generate Flashcards
            </h2>

            <form onSubmit={handleGenerate}>
              <div className="form-group">
                <label className="label">Select Document</label>
                <select
                  className="select"
                  value={selectedDoc}
                  onChange={(e) => setSelectedDoc(e.target.value)}
                  required
                >
                  <option value="">Choose a document</option>
                  {documents.map((doc) => (
                    <option key={doc._id} value={doc._id}>
                      {doc.file_name} ({doc.subject_name})
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="label">Number of Cards (5-10)</label>
                <input
                  type="number"
                  className="input"
                  min="5"
                  max="10"
                  value={numCards}
                  onChange={(e) => setNumCards(Number(e.target.value))}
                />
                <small style={{ color: 'var(--text-secondary)', marginTop: '8px', display: 'block' }}>
                  50% Key Points • 30% Concepts • 20% Comparisons
                </small>
              </div>

              <button
                type="submit"
                className="button button-primary"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader size={20} className="spinning" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles size={20} />
                    Generate Flashcards
                  </>
                )}
              </button>
            </form>
          </div>

          <div className="card">
            <h2 className="card-title">📖 Flashcard Types</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '16px' }}>
              <div className="info-card">
                <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  📌 Key Points (50%)
                </h4>
                <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
                  Concise revision points with 3-5 bullet points per topic. Perfect for quick exam prep.
                </p>
              </div>

              <div className="info-card">
                <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  💡 Concepts (30%)
                </h4>
                <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
                  Simple explanations of core concepts in 40 words or less. Great for understanding basics.
                </p>
              </div>

              <div className="info-card">
                <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  ⚖️ Comparisons (20%)
                </h4>
                <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
                  Side-by-side comparison of commonly confused concepts. Helps clarify differences.
                </p>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="flashcard-viewer">
          <div className="flashcard-progress">
            <span className="progress-text">
              Card {currentIndex + 1} of {flashcards.length}
            </span>
            <button className="reset-button" onClick={handleReset} title="Reset to first card">
              <RotateCcw size={16} />
              Reset
            </button>
          </div>

          <div className="flashcard-container">
            {renderFlashcard(flashcards[currentIndex])}
          </div>

          <div className="flashcard-navigation">
            <button
              onClick={handlePrevious}
              className="button button-secondary"
              disabled={currentIndex === 0}
              style={{ opacity: currentIndex === 0 ? 0.5 : 1 }}
            >
              <ChevronLeft size={20} />
              Previous
            </button>

            <div className="card-dots">
              {flashcards.map((_, idx) => (
                <button
                  key={idx}
                  className={`card-dot ${idx === currentIndex ? 'active' : ''} ${
                    flashcards[idx].type === 'key_point' ? 'key-point' :
                    flashcards[idx].type === 'concept' ? 'concept' : 'comparison'
                  }`}
                  onClick={() => setCurrentIndex(idx)}
                  title={`Card ${idx + 1}: ${flashcards[idx].type}`}
                />
              ))}
            </div>

            <button
              onClick={handleNext}
              className="button button-primary"
              disabled={currentIndex === flashcards.length - 1}
              style={{ opacity: currentIndex === flashcards.length - 1 ? 0.5 : 1 }}
            >
              Next
              <ChevronRight size={20} />
            </button>
          </div>

          <button
            onClick={() => setFlashcards([])}
            className="button button-secondary"
            style={{ marginTop: '24px' }}
          >
            Generate New Flashcards
          </button>
        </div>
      )}

      <style>{`
        .flashcard-viewer {
          max-width: 900px;
          margin: 0 auto;
        }

        .flashcard-progress {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
          padding: 12px 16px;
          background: var(--bg-card);
          border: 1px solid var(--border-color);
          border-radius: 8px;
        }

        .progress-text {
          font-weight: 600;
          color: var(--text-primary);
        }

        .reset-button {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 6px 12px;
          background: var(--bg-tertiary);
          border: 1px solid var(--border-color);
          border-radius: 6px;
          color: var(--text-secondary);
          font-size: 14px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .reset-button:hover {
          background: var(--hover-bg);
          color: var(--text-primary);
        }

        .flashcard-container {
          min-height: 400px;
          margin-bottom: 24px;
        }

        .flashcard-content {
          background: var(--bg-card);
          border: 2px solid var(--border-color);
          border-radius: 16px;
          padding: 32px;
          min-height: 400px;
          display: flex;
          flex-direction: column;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .card-type-badge {
          align-self: flex-start;
          padding: 8px 16px;
          background: rgba(59, 130, 246, 0.1);
          color: var(--accent-blue);
          border-radius: 20px;
          font-size: 14px;
          font-weight: 600;
          margin-bottom: 24px;
        }

        .flashcard-topic {
          font-size: 28px;
          font-weight: 700;
          color: var(--text-primary);
          margin-bottom: 24px;
          text-align: center;
        }

        .flashcard-question {
          font-size: 24px;
          font-weight: 600;
          color: var(--text-primary);
          margin-bottom: 24px;
          text-align: center;
        }

        .key-points-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .key-point-item {
          display: flex;
          gap: 16px;
          align-items: flex-start;
          padding: 16px;
          background: var(--bg-tertiary);
          border-radius: 12px;
          border-left: 4px solid var(--accent-blue);
        }

        .point-number {
          flex-shrink: 0;
          width: 32px;
          height: 32px;
          background: var(--accent-blue);
          color: white;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          font-size: 16px;
        }

        .point-text {
          flex: 1;
          font-size: 16px;
          line-height: 1.6;
          color: var(--text-primary);
        }

        .concept-answer {
          background: var(--bg-tertiary);
          padding: 24px;
          border-radius: 12px;
          border-left: 4px solid var(--accent-purple);
        }

        .concept-answer p {
          font-size: 18px;
          line-height: 1.8;
          color: var(--text-primary);
          margin: 0;
        }

        .comparison-grid {
          display: grid;
          grid-template-columns: 1fr auto 1fr;
          gap: 24px;
          align-items: start;
        }

        .comparison-side {
          background: var(--bg-tertiary);
          padding: 20px;
          border-radius: 12px;
        }

        .comparison-side h3 {
          font-size: 18px;
          font-weight: 600;
          color: var(--accent-blue);
          margin-bottom: 16px;
          text-align: center;
        }

        .comparison-side ul {
          list-style: none;
          padding: 0;
          margin: 0;
        }

        .comparison-side li {
          padding: 10px 0;
          border-bottom: 1px solid var(--border-color);
          font-size: 15px;
          line-height: 1.6;
        }

        .comparison-side li:last-child {
          border-bottom: none;
        }

        .vs-divider {
          background: var(--accent-purple);
          color: white;
          width: 48px;
          height: 48px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          font-size: 14px;
          align-self: center;
        }

        .flashcard-navigation {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 16px;
        }

        .card-dots {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
          justify-content: center;
          flex: 1;
          max-width: 400px;
        }

        .card-dot {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          border: 2px solid var(--border-color);
          background: transparent;
          cursor: pointer;
          transition: all 0.2s;
          padding: 0;
        }

        .card-dot.active {
          width: 32px;
          border-radius: 6px;
        }

        .card-dot.key-point.active {
          background: var(--accent-blue);
          border-color: var(--accent-blue);
        }

        .card-dot.concept.active {
          background: var(--accent-purple);
          border-color: var(--accent-purple);
        }

        .card-dot.comparison.active {
          background: var(--accent-green);
          border-color: var(--accent-green);
        }

        .card-dot:hover:not(.active) {
          border-color: var(--accent-blue);
          transform: scale(1.2);
        }

        .info-card {
          padding: 16px;
          background: var(--bg-tertiary);
          border-radius: 8px;
          border-left: 4px solid var(--accent-blue);
        }

        @media (max-width: 768px) {
          .comparison-grid {
            grid-template-columns: 1fr;
            gap: 16px;
          }

          .vs-divider {
            width: 100%;
            height: auto;
            padding: 8px;
            border-radius: 8px;
          }

          .flashcard-navigation {
            flex-direction: column;
          }

          .card-dots {
            max-width: 100%;
          }
        }
      `}</style>
    </div>
  );
};

export default Flashcards;
