import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
const API_BASE = `${BACKEND_URL}/api/v1`;

class APIClient {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include auth token
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async register(name, email, password) {
    try {
      console.log('API: Sending register request to', `${API_BASE}/auth/register`);
      console.log('API: Register data:', { name, email, password: '***' });
      const response = await this.client.post('/auth/register', { name, email, password });
      console.log('API: Register response:', response.data);
      return response.data;
    } catch (error) {
      console.error('API: Register failed:', error);
      console.error('API: Error response:', error.response);
      throw error;
    }
  }

  async login(email, password) {
    const response = await this.client.post('/auth/login', new URLSearchParams({
      username: email,
      password: password,
    }), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  }

  async getMe() {
    const response = await this.client.get('/auth/me');
    return response.data;
  }

  // Document endpoints
  async uploadDocument(file, subjectName) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('subject_name', subjectName);

    const response = await this.client.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async getDocuments(skip = 0, limit = 20) {
    const response = await this.client.get(`/documents?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async getDocument(documentId) {
    const response = await this.client.get(`/documents/${documentId}`);
    return response.data;
  }

  async deleteDocument(documentId) {
    await this.client.delete(`/documents/${documentId}`);
  }

  // RAG endpoints
  async askQuestion(question, documentId, subject) {
    const response = await this.client.post('/rag/ask', {
      question,
      document_id: documentId,
      subject,
    });
    return response.data;
  }

  // Summary endpoints
  async generateSummary(documentId, summaryType) {
    const response = await this.client.post('/summary/generate', {
      document_id: documentId,
      summary_type: summaryType,
    });
    return response.data;
  }

  async getDocumentSummaries(documentId) {
    const response = await this.client.get(`/summary/document/${documentId}`);
    return response.data;
  }

  async getSummary(summaryId) {
    const response = await this.client.get(`/summary/${summaryId}`);
    return response.data;
  }

  // Quiz endpoints
  async generateQuiz(documentId, numMcq, numShort, numLong) {
    const response = await this.client.post('/quiz/generate', {
      document_id: documentId,
      num_mcq: numMcq,
      num_short: numShort,
      num_long: numLong,
    });
    return response.data;
  }

  async submitQuiz(quizId, answers) {
    const response = await this.client.post('/quiz/submit', {
      quiz_id: quizId,
      answers,
    });
    return response.data;
  }

  async getQuiz(quizId) {
    const response = await this.client.get(`/quiz/${quizId}`);
    return response.data;
  }

  async getQuizResult(resultId) {
    const response = await this.client.get(`/quiz/result/${resultId}`);
    return response.data;
  }

  // Flashcard endpoints
  async generateFlashcards(documentId, numCards) {
    const response = await this.client.post('/flashcard/generate', {
      document_id: documentId,
      num_cards: numCards,
    });
    return response.data;
  }

  async getDocumentFlashcards(documentId) {
    const response = await this.client.get(`/flashcard/document/${documentId}`);
    return response.data;
  }

  // Analytics endpoints
  async getAnalytics() {
    const response = await this.client.get('/analytics');
    return response.data;
  }

  async getDashboard() {
    const response = await this.client.get('/analytics/dashboard');
    return response.data;
  }

  // Learning endpoints
  async generateStudyPlan() {
    const response = await this.client.post('/learning/study-plan');
    return response.data;
  }

  async getStudyPlan() {
    const response = await this.client.get('/learning/study-plan');
    return response.data;
  }

  async getProgress() {
    const response = await this.client.get('/learning/progress');
    return response.data;
  }
}

export const api = new APIClient();
