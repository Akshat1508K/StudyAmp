import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Upload, FileText, CheckCircle, AlertCircle, Loader, Trash2 } from 'lucide-react';
import './UploadDocuments.css';

const UploadDocuments = () => {
  const [file, setFile] = useState(null);
  const [subjectName, setSubjectName] = useState('');
  const [uploading, setUploading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const response = await api.getDocuments();
      setDocuments(response.documents || []);
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type === 'application/pdf') {
        setFile(selectedFile);
        setMessage(null);
      } else {
        setMessage({ type: 'error', text: 'Only PDF files are allowed' });
      }
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file || !subjectName) {
      setMessage({ type: 'error', text: 'Please select a file and enter subject name' });
      return;
    }

    setUploading(true);
    setMessage(null);

    try {
      await api.uploadDocument(file, subjectName);
      setMessage({ type: 'success', text: 'Document uploaded successfully!' });
      setFile(null);
      setSubjectName('');
      loadDocuments();
      
      // Clear file input
      const fileInput = document.getElementById('file-upload');
      if (fileInput) fileInput.value = '';
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Upload failed' });
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      await api.deleteDocument(docId);
      setMessage({ type: 'success', text: 'Document deleted successfully' });
      loadDocuments();
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to delete document' });
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={20} className="status-icon success" />;
      case 'processing':
        return <Loader size={20} className="status-icon processing spinning" />;
      case 'failed':
        return <AlertCircle size={20} className="status-icon error" />;
      default:
        return <Loader size={20} className="status-icon" />;
    }
  };

  return (
    <div className="upload-page">
      <div className="page-header">
        <h1 className="page-title">Upload Study Material</h1>
        <p className="page-subtitle">Upload PDF documents to start learning</p>
      </div>

      {message && (
        <div className={`alert alert-${message.type}`}>
          {message.type === 'error' ? <AlertCircle size={20} /> : <CheckCircle size={20} />}
          <span>{message.text}</span>
        </div>
      )}

      <div className="grid grid-2">
        <div className="card upload-card">
          <h2 className="card-title">
            <Upload size={20} />
            Upload New Document
          </h2>

          <form onSubmit={handleUpload} className="upload-form">
            <div className="file-upload-area">
              <input
                type="file"
                id="file-upload"
                accept=".pdf"
                onChange={handleFileChange}
                className="file-input"
              />
              <label htmlFor="file-upload" className="file-upload-label">
                <FileText size={48} />
                <div className="file-upload-text">
                  <span className="file-upload-title">
                    {file ? file.name : 'Choose a PDF file'}
                  </span>
                  <span className="file-upload-subtitle">
                    Click to browse or drag and drop
                  </span>
                </div>
              </label>
            </div>

            <div className="form-group">
              <label htmlFor="subject" className="label">Subject Name</label>
              <input
                id="subject"
                type="text"
                className="input"
                placeholder="e.g., Database Management Systems"
                value={subjectName}
                onChange={(e) => setSubjectName(e.target.value)}
                required
              />
            </div>

            <button
              type="submit"
              className="button button-primary button-full"
              disabled={uploading || !file}
            >
              {uploading ? (
                <>
                  <Loader size={20} className="spinning" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload size={20} />
                  Upload Document
                </>
              )}
            </button>
          </form>
        </div>

        <div className="card info-card">
          <h2 className="card-title">📋 Instructions</h2>
          <ul className="info-list">
            <li>Only PDF files are supported</li>
            <li>Maximum file size: 50MB</li>
            <li>Use clear and descriptive subject names</li>
            <li>Ensure PDFs are text-based (not scanned images)</li>
            <li>Processing may take a few moments</li>
          </ul>
        </div>
      </div>

      <div className="card documents-card">
        <h2 className="card-title">
          <FileText size={20} />
          Your Documents
        </h2>

        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
          </div>
        ) : documents.length > 0 ? (
          <div className="documents-grid">
            {documents.map((doc) => (
              <div key={doc._id} className="document-card">
                <div className="document-header">
                  <FileText size={24} />
                  {getStatusIcon(doc.processing_status)}
                </div>
                <div className="document-body">
                  <h3 className="document-title">{doc.file_name}</h3>
                  <div className="document-subject">{doc.subject_name}</div>
                  <div className="document-meta">
                    <span>
                      {new Date(doc.upload_date).toLocaleDateString()}
                    </span>
                    {doc.total_pages && <span>• {doc.total_pages} pages</span>}
                    {doc.total_chunks && <span>• {doc.total_chunks} chunks</span>}
                  </div>
                </div>
                <div className="document-footer">
                  <span className={`status-badge ${doc.processing_status}`}>
                    {doc.processing_status}
                  </span>
                  <button
                    className="icon-btn danger"
                    onClick={() => handleDelete(doc._id)}
                    title="Delete document"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <FileText size={64} />
            <p>No documents uploaded yet</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadDocuments;
